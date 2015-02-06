#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : verify_prediction.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Verify prediction file against popular datasets
"""

# system modules
import optparse

# local modules
from DCAF.utils.utils import fopen

class OptionParser():
    def __init__(self):
        "User based option parser"
        usage  = 'Usage: %prog [options]\n'
        usage += 'Description: verify prediction file against popular dataset one retrieved from popularity DB\n'
        usage += 'Example: %prog --pred=pred.txt.out --popdb=popdb-20150101-20150108.txt'
        self.parser = optparse.OptionParser(usage=usage)
        self.parser.add_option("--pred", action="store", type="string",
            dest="pred", default="", help="Input prediction file")
        self.parser.add_option("--popdb", action="store", type="string",
            dest="popdb", default="", help="Input popular datasets file")
        self.parser.add_option("--verbose", action="store", type="int",
            dest="verbose", default=False, help="verbose mode")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def read_popdb(popdb):
    "Read popdb data"
    headers = []
    pdict = {}
    with fopen(popdb, 'r') as istream:
        while True:
            if  not headers:
                for row in istream.readline().replace('\n', '').split(','):
                    if  row == 'COLLNAME':
                        headers.append('dataset')
                    elif row == 'NACC':
                        headers.append('naccess')
                    elif row == 'RNACC':
                        headers.append('rnaccess')
                    else:
                        headers.append(row.lower())
                continue
            vals = istream.readline().replace('\n', '').split(',')
            if  len(vals) < 2:
                break
            row = dict(zip(headers, vals))
            dataset = row.pop('dataset')
            pdict[dataset] = row
    return pdict

def metrics(tpos, tneg, fpos, fneg):
    "Return accuracy, precision, recall, f1score"
    try:
        accuracy = float(tpos+tneg)/float(tpos+tneg+fpos+fneg)
    except:
        accuracy = 0
    try:
        precision = float(tpos)/float(tpos+fpos)
    except:
        precision = 0
    try:
        recall = float(tpos)/float(tpos+fneg)
    except:
        recall = 0
    try:
        f1score = 2*precition*recall/(precition+recall)
    except:
        f1score = 0
    return accuracy, precision, recall, f1score

def classify(datasets):
    "Classify datasets"
    tiers = {}
    for dataset in datasets:
        _, prim, proc, tier = dataset.split('/')
        if  tier in tiers:
            tiers[tier] += 1
        else:
            tiers[tier] = 1
    pairs = [(v, k) for k, v in tiers.items()]
    width = ''
    pairs.sort()
    pairs.reverse()
    for key, val in pairs:
        if  not width:
            width = len(str(key))+1
        print '%s %s %s'  % (key, ' '*(width-len(str(key))), val)

def verify_prediction(pred, popdb, verbose=0):
    "Verify prediction file against popdb one"
    pdict = read_popdb(popdb)
    total = 0
    popular = 0
    totpop = 0
    tpos = 0
    tneg = 0
    fpos = 0
    fneg = 0
    fp_list = []
    fn_list = []
    for line in fopen(pred, 'r').readlines():
        prob, dataset = line.replace('\n', '').split(',')
        total += 1
        if  float(prob)>0:
            popular += 1
        if  dataset in pdict:
            totpop += 1
            if  verbose>1:
                naccess = pdict[dataset]['naccess']
                nusers = pdict[dataset]['nusers']
                print 'prob=%s nacc=%s nusers=%s %s' % (prob, naccess, nusers, dataset)
            if  float(prob)>0:
                tpos += 1
            else:
                fneg += 1
        else:
            if  float(prob)>0:
                fpos += 1
                fp_list.append(dataset)
            else:
                tneg += 1
                fn_list.append(dataset)
    accuracy, precision, recall, f1score = metrics(fpos, tneg, fpos, fneg)
    print "# dataset in popdb sample :", len(pdict.keys())
    print "# datasets we predict     :", total
    print "# datasets in popular set :", totpop
    print "Predicted as popular      :", popular
    print
    def perc(vvv):
        return '%s%%' % round(vvv*100./total, 1)
    def space(vvv):
        return '%s%s' % (vvv, ' '*(len(str(total))-len(str(vvv))))
    print "True positive             : %s, %s" % (space(tpos), perc(tpos))
    print "True negative             : %s, %s" % (space(tneg), perc(tneg))
    print "False positive            : %s, %s" % (space(fpos), perc(fpos))
    print "False negative            : %s, %s" % (space(fneg), perc(fneg))
    print
    if  verbose:
        print "Classification of FP sample"
        classify(fp_list)
        print "Classification of FN sample"
        classify(fn_list)
    print "Accuracy                  :", accuracy
    print "Precision                 :", precision
    print "Recall                    :", recall
    print "F1-score                  :", f1score

def main():
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    verify_prediction(opts.pred, opts.popdb, opts.verbose)

if __name__ == '__main__':
    main()
