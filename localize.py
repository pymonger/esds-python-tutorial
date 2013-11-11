#!/usr/bin/env python
import os, shutil, time
from glob import glob

def main():
    """Simulate localizing remote data to our staging area."""

    data_dir = "/data/demo_data"
    stage_dir = "/data/public/staging"

    for i in glob(os.path.join(data_dir, "AIRS*.hdf")):
        basename = os.path.basename(i)
        stage_file = os.path.join(stage_dir, basename)
        signal_file = os.path.join(stage_dir, "%s.done" % basename)
        shutil.move(i, stage_file)
        with open(signal_file, 'w') as f:
            f.write('DONE')
        print "staged %s to %s" % (i, stage_file)
        #time.sleep(1)

if __name__ == "__main__": main()
