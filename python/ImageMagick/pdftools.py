# Licensed under a 3-clause BSD style license - see LICENSE
# Copyright Todd Hunter

import os, glob
from filetools import pruneFilelist

def concatenatePDFs(filelist, pdfname, pdftk='pdftk', gs='gs', cleanup=False,
                    quiet=False):
    """
    Takes a list or a string list of PDF filenames (space-delimited), and an
    output name, and concatenates them.
    It first tries pdftk (better quality), and if that fails, it tries
    ghostscript (more commonly installed).
    Todd Hunter
    """
    if (type(filelist) == list):
        filelist = ' '.join(filelist)
    cmd = '%s %s cat output %s' % (pdftk, filelist, pdfname)
    if not quiet: print "Running command = %s" % (cmd)
    mystatus = os.system(cmd)
    if (mystatus != 0):
        print "status = ", mystatus
        cmd = '%s -q -sPAPERSIZE=letter -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=%s %s' % (gs,pdfname,filelist)
        print "Running command = %s" % (cmd)
        mystatus = os.system(cmd)
        if (mystatus != 0):
            gs = '/opt/local/bin/gs'
            cmd = '%s -q -sPAPERSIZE=letter -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=%s %s' % (gs,pdfname,filelist)
            print "Running command = %s" % (cmd)
            mystatus = os.system(cmd)
            if (mystatus != 0):
                print "Both pdftk and gs are missing, no PDF created."
                cleanup = False
    if (cleanup):
        os.system('rm %s' % filelist)
    return (mystatus)

def buildPdfFromPngs(pnglist=[],pdfname='',convert='convert',gs='gs',
                     pdftk='pdftk',maxcount=0,cleanup=True,quiet=False):
    """
    Will convert a list of PNGs into PDF, then concatenate them into one PDF.
    Arguments:
    pnglist: list of PNG files ['a.png','b.png'], or a string which is assumed
             to be a directory in which all *.png's will be grabbed.  If this
             string contains a *, it will not assume that it is a wildcard
             string with which to identify files as pngs to grab.
    pdfname:  the filename to produce (default = my.pdf)
    convert: specify full path to ImageMagick's convert command (if necessary)
    gs:  specify the full path to ghostscript's gs command (if necessary)
    pdftk: specify the full path to the pdftk command (if necessary)
    maxcount: maximum number of files to include
    cleanup: remove the temporary single-page PDFs
    """
    filelist = ''
    if (type(pnglist) == str):
        # assume we want all pngs in this directory
        if (pnglist.find('*') < 0):
            pnglist = sorted(glob.glob(pnglist+'/*.png'))
        else:
            pnglist = sorted(glob.glob(pnglist))
            if not quiet: print "pnglist = ", pnglist
    if (len(pnglist) < 1):
        return("You must specify at least one file with pnglist=['myfile1','myfile2',...].")
    pnglist = pruneFilelist(pnglist)
    if not quiet: print "Pruned list = ", pnglist
    count = 0
    for p in pnglist:
        if (maxcount > 0 and count >= maxcount): break
        count += 1
#        print "Checking if I have write privilege on %s" % (p)
        if (os.access(p,os.W_OK)):
            onepdf = '%s.pdf' % (p)
        else:
            onepdf = '/tmp/%s.pdf' % (p.split('/')[-1])
        cmd = '%s %s %s' % (convert,p,onepdf)
        if not quiet: print "Running command = ", cmd
        mystatus = os.system(cmd)
        if (mystatus == 0):
            filelist += onepdf + ' '
        elif (mystatus == 256):
            return("Could not find one or more of the png files.")
        else:
            # MacOS location of convert
            convert = '/opt/local/bin/convert'
            cmd = '%s %s %s' % (convert, p,onepdf)
            if not quiet: print "Running command = ", cmd
            mystatus = os.system(cmd)
            if (mystatus == 0):
                filelist += onepdf + ' '
            elif (mystatus == 256):
                return("Could not find one or more of the png files.")
            else:
                mystring = "ImageMagick's convert command is missing, no PDF created. You can set the full path to convert with convert=''"
                return(mystring)
    if (pdfname == ''):
        pdfname = './my.pdf'
    if (os.path.dirname(pdfname) == ''):
        pdfname = './' + pdfname
    mypath = os.path.dirname(pdfname)
    print "Checking if I have write privilege on %s." % (mypath)
    if (os.access(mypath, os.W_OK) == False):
#        print "no"
        pdfname = '/tmp/%s' % (os.path.basename(pdfname))
    else:
        pdfname = pruneFilelist([pdfname])[0]
        
#    else:
#        print "yes"
    if (len(pnglist) > 1):
        mystatus = concatenatePDFs(filelist,pdfname,pdftk=pdftk,gs=gs,quiet=quiet)
    else:
        cmd = 'cp %s %s' % (filelist,pdfname)
        print "Running command = %s" % (cmd)
        mystatus = os.system(cmd)
    if (mystatus == 0):
        print "PDF left in %s" % (pdfname)
        if (cleanup):
            os.system("rm -f %s" % filelist)
    else:
        print "No PDF created. pdftk and gs (ghostscript) might both be missing"
        print "If so, you can set the full path to pdftk with pdftk='', or to gs with gs=''"
    return('')
# end of buildPdfsFromPngs

