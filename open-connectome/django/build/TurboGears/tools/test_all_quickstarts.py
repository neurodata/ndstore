#!/usr/bin/env python

import os
import shutil
import sys

def run_all():
    qs_variants = (
        ('SAIdentity', '-i -s'),
        ('SANoIdentity', '--no-identity -s'),
        ('SOIdentity', '-i -o'),
        ('SONoIdentity', '--no-identity -o'),
        ('ElIdentity', '-i -e'),
        ('ElNoIdentity', '--no-identity -e')
    )

    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = None

    for variant, options in qs_variants:
        if choice and variant != choice:
            print "Skipping quickstart variant %s..." % variant
            continue
        if os.path.isdir(variant):
            shutil.rmtree(variant)
        os.system('tg-admin quickstart %s -p %s %s' % (options, variant.lower(), variant))
        os.chdir(variant)
        try:
            os.system('python setup.py develop')
            os.system('python setup.py test')
            if '-i ' in options:
                os.system('bootstrap-%s -u test' % variant.lower())
            os.system('python start-%s.py'% variant.lower())
            raw_input("Hit ENTER to continue...")
            print
        finally:
            os.chdir('..')
            if os.path.isdir(variant):
                shutil.rmtree(variant)

def main():
    if not os.path.isdir('tgquicktest'):
        os.mkdir('tgquicktest')
    os.chdir('tgquicktest')
    try:
        run_all()
    finally:
        os.chdir('..')
        if os.path.isdir('tgquicktest'):
            shutil.rmtree('tgquicktest')

if __name__ == '__main__':
    main()
