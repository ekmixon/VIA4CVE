#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Source file for saint exploit information
#
# Software is free software released under the "Modified BSD license"
#
# Copyright (c) 2016    Pieter-Jan Moreels - pieterjan.moreels@gmail.com

# Sources
SOURCE_NAME = 'saint'
SOURCE_FILE = "https://my.saintcorporation.com/xml/exploits.xml"

# Imports
import copy

from collections     import defaultdict
from io              import BytesIO
from xml.sax         import make_parser
from xml.sax.handler import ContentHandler

from lib.Config import Configuration as conf
from lib.Source import Source

class SaintHandler(ContentHandler):
  def __init__(self):
    self.exploits = []
    self.saint    = None
    self.tag      = None

  def startElement(self, name, attrs):
    self.tag = name
    if   name == 'exploit':
      self.saint={}
      if attrs.get('id'): self.saint['title']=attrs.get('id')

  def characters(self, ch):
    if self.tag == 'saint_id': self.saint['id']     = ch
    elif self.tag and self.tag != "exploit" and self.saint and ch:
      self.saint[self.tag] = ch

  def endElement(self, name):
    self.tag = None
    if   name == 'exploit' and self.saint:
      self.exploits.append(self.saint)
      self.saint = None


class Saint(Source):
  def __init__(self):
    self.name = SOURCE_NAME
    parser    = make_parser()
    handler = SaintHandler()
    _file, r = conf.getFeedData(SOURCE_NAME, SOURCE_FILE)
    parser.setContentHandler(handler)
    parser.parse(BytesIO(_file))
    self.cves   = defaultdict(list)
    self.bids   = defaultdict(list)
    self.osvdbs = defaultdict(list)
    for exploit in handler.exploits:
      data = copy.copy(exploit)
      if data.get('cve'): data.pop('cve')
      if exploit.get('cve'):   self.cves[  exploit['cve']  ].append(data)
      if exploit.get('bid'):   self.bids[  exploit['bid']  ].append(data)
      if exploit.get('osvdb'): self.osvdbs[exploit['osvdb']].append(data)

  def updateRefs(self, cveID, cveData):
    cveData['saint'] = []
    # Map osvdb, bid and cve
    _bids   = cveData.get('refmap', {}).get('bid',   {})
    _osvdbs = cveData.get('refmap', {}).get('osvdb', {})
    cveData['saint'].extend(self.cves[cveID])

    for bid   in _bids:   cveData['saint'].extend(self.bids[bid])
    for osvdb in _osvdbs: cveData['saint'].extend(self.osvdbs[osvdb])
    # make unique
    cveData['saint'] = [
        dict(t) for t in {tuple(d.items())
                          for d in cveData['saint']}
    ]
    # remove if empty
    if cveData['saint'] == []: cveData.pop('saint')

  def getSearchables(self):
    return ['id', 'bid', 'osvdb', 'title']
