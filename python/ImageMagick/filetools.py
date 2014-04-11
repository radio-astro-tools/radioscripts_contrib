def pruneFilelist(filelist):
    """
    Reduce size of filenames in filelist to the extent that current working
    directory agrees with the path.
    """
    mypwd = os.getcwd() + '/'
    newfilelist = []
    for f in filelist:
        fstart = 0
        if (f.find(mypwd) == 0):
            fstart = len(mypwd)
        newfilelist.append(f[fstart:])
    return(newfilelist)
    
