#! /usr/bin/python3

# hhu-mediathek-dl: Download or stream lecture videos from http://mediathek.hhu.de
#
# Copyright (C) 2014 Ludger Sandig
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import sys
import urllib.request
import re
import subprocess
import pprint

# For verbose printing. Define it to do noting for now, the __main__
# function may change it to print depending on the commandline
# arguments.

verboseprint = lambda *a, **k: None

# Parse command line argv arguments, return them parsed.

def parseArguments( argv ):
    description="Download or view lecture from mediathek.hhu.de"
    name = argv[0]
    epilog = "Please note: The options -d and -s are mutually exclusive for now!"
    
    parser = argparse.ArgumentParser( description=description, prog=name, epilog=epilog )
    actions = parser.add_mutually_exclusive_group()
    
    parser.add_argument( "url", help="url to the video's page" )
    actions.add_argument( "-d", "--download", action="store_const", dest="action", const="download", help="save the file to disk (default)")
    actions.add_argument( "-s", "--stream", action="store_const", dest="action", const="stream", help="stream the video with the program given by `--player`")
    parser.set_defaults( action="download" )

    parser.add_argument( "-q", "--quality", choices=["low", "medium", "high"], metavar="<low/medium/high>", default="high" )
    parser.add_argument( "-f", "--format", choices=["mp4","webm"], metavar="<mp4/webm>", default="mp4" )

    parser.add_argument( "-o", "--output", help="where to save the downloaded file; default: current directory with video's title", default="" )
    parser.add_argument( "--player", help="which videoplayer to use; default: mplayer", default="mplayer"  )
    parser.add_argument( "-v", "--verbose", action="store_true", default=False )
    
    # TODO: Strange things happen when parse_args( argv ) is called
    return parser.parse_args( )

# Get the videos html page. This can go wrong in many ways, catch two
# of them: args.url is no url, any http errors
# On success, return page as string

def fetchVideopage( url ):
    verboseprint( "Fetching: %s" % url )
    
    try:
        page = urllib.request.urlopen( url ).read().decode("utf-8")
    except ( ValueError, urllib.error.HTTPError ) as e:
        print( "Error: could not fetch page" )
        print( e )
        exit(1)
    return page


# Now the fun part, extract the urls to the videos The page source
# contains some javascript that loads the player. In there it says:
# 
# sources: [
#
# { file: '/movies/7d89feaca4fc42cda8080f3552ec05b7/v_100.mp4', width:
# 1280, height: 720, label: 'hohe Qualität' },
#
# { file: '/movies/7d89feaca4fc42cda8080f3552ec05b7/v_100.webm',
# width: 1280, height: 720, label: 'hohe Qualität' },
#
# { file: '/movies/7d89feaca4fc42cda8080f3552ec05b7/v_50.mp4', width:
# 854, height: 480, label: 'mittlere Qualität' },
#
# { file: '/movies/7d89feaca4fc42cda8080f3552ec05b7/v_50.webm', width:
# 854, height: 480, label: 'mittlere Qualität' },
#
# { file: '/movies/7d89feaca4fc42cda8080f3552ec05b7/v_10.mp4', width:
# 640, height: 360, label: 'niedrige Qualität' },
#
# { file: '/movies/7d89feaca4fc42cda8080f3552ec05b7/v_10.webm', width:
# 640, height: 360, label: 'niedrige Qualität' }
#
# ],
#
# We will take the ugly solution and grep for
# '/movies/<somestring>/v_<x>.<format>'
#
# Return a list of dictionarys of the form:
#
# {"url": "http://mediathek.hhu.de/movies/<something>/filename", "id":
# "<something>" "format" : "mp4|webm", "quality" : "l|m|h" }

def extractVideoLinks( page ):
    links = re.findall( "(/movies/([a-z0-9]*)/v_(10|50|100).(mp4|webm))", page )

    li = []

    for match in links:
        url = "http://mediathek.hhu.de" + match[0]
        vid = match[1]
        if( match[2] == "10" ):
            quality = "low"
        elif( match[2] == "50"):
            quality = "medium"
        elif( match[2] == "100"):
            quality = "high"
        vformat = match[3]
        li.append( { "url" : url, "id" : vid, "quality" : quality, "format" : vformat } )

    verboseprint( "Found %d video links:" % len( links ) )
    verboseprint( "--------------------" )
    for l in li:
        pretty = pprint.pformat( l )
        verboseprint( pretty )
    verboseprint( "--------------------" )
    return li

# return the dict from links where quality and format match q and
# f. If none matches, return any.
def selectVideoLink( links, q, f ):
    for d in links:
        if( d["format"] == f and d["quality"] == q ):
            return d
    # Not found
    d = links[0]
    print( "Warning: Desired format/quality combination not available.\n\tRun with --verbose switch to see alternatives." )
    print( "\tFor now using format = '%s' and quality = '%s'" % (d["format"], d["quality"]) )
    return d

# Run program with url
# TODO: As program can be user-supplied it might need to be sanitized
def streamVideo( program, url ):
    print( "Running: '%s %s'" % (program, url) )
    subprocess.call( [program, url] )


# Extract title from video's html page
def extractTitle( page ):
    regex = re.compile('<meta property="og:title" content="(.*)" />')
    return regex.search( page ).groups()[0]

# Construct filename from title and video info
# Returns "[title|id]_<quality>.<format>"
def makeFilename( title, info  ):
    if( not title == "" ):
        # remove leading and trailing whitespace
        base = title.strip()
        # remove all non-word chars except "-"
        base = re.sub( "[^\w\s\-]", "", base )
        # replace all (also multiple) whitespace with exactly one underscore
        base = re.sub( "\s+", "_", base )
        # convert to lower case
        base = base.lower()
    else:
        base = info["id"]
    return base + "_" + info["quality"] + "." + info["format"]

# Function for the download reporthook. Print completion in % and MB
def report( count, size, total ):
    percent = count * size * 100 / total
    mb = count * size / 1024 / 1024
    totalmb = total / 1024 / 1024
    sys.stdout.write( "\rDownload at %02.1f%% (%.1fMiB/%.1fMiB)" % (percent, mb, totalmb ) )
    sys.stdout.flush()

if( __name__ == "__main__" ):

    # Parse command line arguments    
    args = parseArguments( sys.argv )

    # Set verbosity
    verboseprint = print if args.verbose else lambda *a, **k: None

    # Get the videopage
    page = fetchVideopage( args.url )

    # Find all (parts of) links to the videos
    links = extractVideoLinks( page )

    # Did we find any?
    if( not links ):
        print( "Error: No video links found!" )
        exit(1)

    # Select video
    vid = selectVideoLink( links, args.quality, args.format )
    if( args.verbose ):
        print( "Selected video: " )
        pprint.pprint( vid )

    # To stream or to save? That is the question:
    if( args.action == "stream" ):
        streamVideo( args.player, vid["url"] )
    elif( args.action == "download" ):
        # Select output filename
        # a) user supplied with --output option
        # b) from video title
        # c) from video id (only if video title cannot be extracted)
        if( not args.output == "" ):
            filename = args.output
            verboseprint( "Filename supplied by user: %s" % filename )
        else:
            # title might be empty
            title = extractTitle( page )
            filename = makeFilename( title, vid )
            verboseprint( "Filename scraped from page: %s" % filename )
        print( "Downloading '%s' to '%s'" % (vid["url"], filename) )
        urllib.request.urlretrieve( vid["url"], filename, reporthook=report )
        print( "\nDone." )
    else:
        # How did you even get here?
        print( "Error: Unknown action: '%s'" % args.action )
    
    exit(0)
