#!/usr/bin/env python

from optparse import OptionParser
import tempfile
import shutil
import os
import subprocess

def main():
  global options
  usage = "usage: %prog [options] in.svg out.svg"
  parser = OptionParser(usage)

  parser.add_option("-v", "--verbose",
      action="store_true", dest="verbose")
  parser.add_option("-q", "--quiet",
      action="store_false", dest="verbose")
  parser.add_option("-t", "--threshold", help="simplification threshold",
      action="store", dest="threshold")

  parser.set_defaults(threshold=0.0001)

  (options, args) = parser.parse_args()

  if len(args)<2:
    parser.error("not enough arguments (got {}, expected 2)".format(len(args)));

  input_file = args[0]
  output_file = args[1]

  shutil.copyfile(input_file,output_file)

  temp_dir = tempfile.mkdtemp()

  inkscape_dir = os.path.join(temp_dir,".config/inkscape") 

  os.makedirs(inkscape_dir)

  preferences_file = os.path.join(inkscape_dir,"preferences.xml");

  f = open(preferences_file,"w")

  f.write("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<inkscape
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   version="1">
  <group
     id="options">
    <group
       id="simplifythreshold"
       value="{}" />
  </group>
</inkscape>
""".format(options.threshold))
  f.close()

  subprocess.call(["/usr/bin/env","HOME={}".format(temp_dir),"inkscape","--verb=EditSelectAll","--verb=SelectionSimplify","--verb=FileSave","--verb=FileQuit",output_file])
  
  #shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()

