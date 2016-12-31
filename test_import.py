"""
Testing maspy high level functions
"""

#  Copyright 2015-2017 David M. Hollenstein, Jakob J. Hollenstein
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

######################### Python 2 and 3 compatibility #########################
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals
from future.utils import viewitems, viewkeys, viewvalues, listitems, listvalues

try:
    #python 2.7
    from itertools import izip as zip
except ImportError:
    #python 3 series
    pass
################################################################################

import sys
sys.path.append('C:/Users/David/Dropbox/python/maspy')
sys.path.append('D:/Dropbox/python/maspy')

import contextlib
import os
import shutil
import tempfile

import maspy.auxiliary as aux
import maspy.core
import maspy.reader


@contextlib.contextmanager
def makeTempDir():
    """Context manager to generate a temp directory and delete it afterwards."""
    tempdir = tempfile.mkdtemp()

    try:
        yield tempdir
    finally:
        shutil.rmtree(tempdir)

def convertMzmlFiles(testfileInfo):
    """Convert the test mzML files into the maspy .mrc format."""
    for specfile in testfileInfo['specfiles']:
        filepath = aux.joinpath(testfileInfo['testfiledir'], specfile + '.mzML')
        maspy.reader.convertMzml(filepath, testfileInfo['tempdir'])

def importMrcFiles(testfileInfo):
    """Import the .mrc files from the temp directory."""
    msrunContainer = maspy.core.MsrunContainer()
    msrunContainer.addSpecfile(testfileInfo['specfiles'],
                               testfileInfo['tempdir'])
    msrunContainer.load()
    return msrunContainer

def convertPercolatorTsv(testfileInfo):
    """Convert the percolator .tsv test files into the maspy .siic format."""
    siiContainer = maspy.core.SiiContainer()
    for specfile in testfileInfo['specfiles']:
        filepath = aux.joinpath(testfileInfo['testfiledir'], specfile,
                                'target_percolator_output.tsv')
        maspy.reader.importPercolatorResults(siiContainer, filepath,
                                             specfile, 'comet')
    siiContainer.save(path=testfileInfo['tempdir'])

def importSiicFiles(testfileInfo):
    """Import the generated .siic test files from the temp directory."""
    siiContainer = maspy.core.SiiContainer()
    siiContainer.addSpecfile(specfiles, testfileInfo['tempdir'])
    siiContainer.load()
    return siiContainer

def convertFeatureXmlFiles(testfileInfo):
    """Convert the OpenMS .featureXML test files."""
    fiContainer = maspy.core.FiContainer()
    for specfile in testfileInfo['specfiles']:
        filepath = aux.joinpath(testfileInfo['testfiledir'],
                                specfile + '.featureXML')
        maspy.reader.importPeptideFeatures(fiContainer, filepath, specfile)
    fiContainer.save(path=testfileInfo['tempdir'])

def importFicFiles(testfileInfo):
    """Import the generated .fic test files from the temp directory."""
    fiContainer = maspy.core.FiContainer()
    fiContainer.addSpecfile(specfiles, testfileInfo['tempdir'])
    fiContainer.load()
    return fiContainer


def main(testfileInfo):
    print('Converting mzML')
    convertMzmlFiles(testfileInfo)
    print('Importing MsrunContainer files')
    msrunContainer = importMrcFiles(testfileInfo)

    print('Converting PSMs')
    convertPercolatorTsv(testfileInfo)
    print('Importing SiiContainer files')
    siiContainer = importSiicFiles(testfileInfo)

    print('Converting Features')
    convertFeatureXmlFiles(testfileInfo)
    print('Importing FiContainer files')
    fiContainer = importFicFiles(testfileInfo)

    siiContainer.addSiInfo(msrunContainer, specfiles=testfileInfo['specfiles'],
                           attributes=['obsMz', 'rt', 'charge', 'precursorId']
                           )
    siiContainer.calcMz()


if __name__ == '__main__':
    rootdir = os.path.dirname(__file__)
    testfiledir = aux.joinpath(rootdir, 'files')
    specfiles = ['JD_06232014_sample1_A',
                 'JD_06232014_sample1_B'][0:1]
    with makeTempDir() as tempdir:
        testfileInfo = {'tempdir': tempdir, 'testfiledir': testfiledir,
                        'specfiles': specfiles}

        print('Starting maspy file import tests.')
        print('---------------------------------')
        main(testfileInfo)

        print('\nAll tests successfull.')
        raw_input('Press enter to delete the temporary directory.')
    
    if os.path.isdir(testfileInfo['tempdir']):
        print('Temporary directory not deleted: ', testfileInfo['tempdir'])
    raw_input('Press enter to quit.')