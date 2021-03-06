#!/usr/bin/python
#
# Tests for specgen.
#
# What is this, and how can you help?
#
# This is the test script for a rewrite of the FOAF spec generation
# tool. It uses Pure python rdflib for parsing. That makes it easier to
# install than the previous tools which required successful compilation
# and installation of Redland and its language bindings (Ruby, Python ...).  
#
# Everything is in public SVN. Ask danbri for an account or password reminder if # you're contributing.
#
# Code: svn co http://svn.foaf-project.org/foaftown/specgen/
#
# Run tests (with verbose flag):
# ./run_tests.py -v
#
# What it does:
#  The FOAF spec is essentially built from an index.rdf file, plus a collection of per-term *.en HTML fragments.
#  This filetree includes a copy of the FOAF index.rdf and markup-fragment files (see examples/foaf/ and examples/foaf/doc/).
# 
# Code overview: 
# 
# The class Vocab represents a parsed RDF vocabulary. VocabReport represents the spec we're generating from a Vocab.
# We can at least load the RDF and poke around it with SPARQL. The ideal target output can be seen by looking at the
# current spec, basically we get to a "Version 1.0" when something 99% the same as the current spec can be built using this
# toolset, and tested as having done so.
# 
# Rough notes follow:
# trying to test using ...
# http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html 
# http://docs.python.org/library/unittest.html

# TODO: convert debug print statements to appropriate testing / verbosity logger API
# TODO: make frozen snapshots of some more namespace RDF files
# TODO: find an idiom for conditional tests, eg. if we have xmllint handy for checking output, or rdfa ...

FOAFSNAPSHOTDIR = 'examples/foaf/'
FOAFSNAPSHOT = 'index-20081211.rdf' # a frozen copy for sanity' sake
DOAPSNAPSHOTDIR = 'examples/doap/'
DOAPSNAPSHOT = 'doap-en.rdf'  # maybe we should use dated url / frozen files for all
SIOCSNAPSHOTDIR = 'examples/sioc/'
SIOCSNAPSHOT = 'sioc.rdf'

import libvocab
from libvocab import Vocab
from libvocab import VocabReport
from libvocab import Term
from libvocab import Class
from libvocab import Property
from libvocab import SIOC
from libvocab import OWL
from libvocab import FOAF
from libvocab import RDFS
from libvocab import RDF
from libvocab import DOAP
from libvocab import XFN

# used in SPARQL queries below
bindings = { u"xfn": XFN, u"rdf": RDF, u"rdfs": RDFS, u"owl": OWL, u"doap": DOAP, u"sioc": SIOC, u"foaf": FOAF }

import rdflib
from rdflib.namespace import Namespace
from rdflib.graph import Graph
from rdflib.graph import ConjunctiveGraph

import unittest

class testSpecgen(unittest.TestCase):

  """a test class for Specgen"""

  def setUp(self):
    """set up data used in the tests. Called  before each test function execution."""

  def testFOAFns(self):
    foaf_spec = Vocab(FOAFSNAPSHOTDIR,FOAFSNAPSHOT)
    foaf_spec.index()
    foaf_spec.uri = FOAF
    # print "FOAF should be "+FOAF
    self.assertEqual(str(foaf_spec.uri), 'http://xmlns.com/foaf/0.1/')

  def testSIOCns(self):
    sioc_spec = Vocab('examples/sioc/','sioc.rdf')
    sioc_spec.index()
    sioc_spec.uri = str(SIOC)
    self.assertEqual(sioc_spec.uri, 'http://rdfs.org/sioc/ns#')

  def testDOAPWrongns(self):
    doap_spec = Vocab('examples/doap/','doap-en.rdf')
    doap_spec.index()
    doap_spec.uri = str(DOAP)
    self.assertNotEqual(doap_spec.uri, 'http://example.com/DELIBERATE_MISTAKE_HERE')

  def testDOAPns(self):
    doap_spec = Vocab('examples/doap/','doap-en.rdf')
    doap_spec.index()
    doap_spec.uri = str(DOAP)
    self.assertEqual(doap_spec.uri, 'http://usefulinc.com/ns/doap#')

  #reading list: http://tomayko.com/writings/getters-setters-fuxors
  def testCanUseNonStrURI(self):
    """If some fancy object used with a string-oriented setter, we just take the string."""
    doap_spec = Vocab('examples/doap/','doap-en.rdf')
    print "[1]"
    doap_spec.index()
    doap_spec.uri = Namespace('http://usefulinc.com/ns/doap#')  # likely a common mistake
    self.assertEqual(doap_spec.uri, 'http://usefulinc.com/ns/doap#')

  def testFOAFminprops(self):
    """Check we found at least 50 FOAF properties."""
    foaf_spec = Vocab('examples/foaf/','index-20081211.rdf')
    foaf_spec.index()
    foaf_spec.uri = str(FOAF)
    c = len(foaf_spec.properties)
    self.failUnless(c > 50 , "FOAF has more than 50 properties. count: "+str(c))

  def testFOAFmaxprops(self):
    foaf_spec = Vocab(dir=FOAFSNAPSHOTDIR, f=FOAFSNAPSHOT, uri = FOAF)
    foaf_spec.index()
    c = len(foaf_spec.properties)
    self.failUnless(c < 100 , "FOAF has less than 100 properties. count: "+str(c))

  def testSIOCmaxprops(self):
    """sioc max props: not more than 500 properties in SIOC"""
    sioc_spec = Vocab(dir='examples/sioc/',f='sioc.rdf')
    sioc_spec.index()
    sioc_spec.uri = str(SIOC)
    c = len(sioc_spec.properties)
    #print "SIOC property count: ",c
    self.failUnless(c < 500 , "SIOC has less than 500 properties. count was "+str(c))


  # work in progress.  
  def testDOAPusingFOAFasExternal(self):
    """when DOAP mentions a FOAF class, the API should let us know it is external"""
    doap_spec = Vocab(dir='examples/doap/',f='doap.rdf')
    doap_spec.index()
    doap_spec.uri = str(DOAP)
    for t in doap_spec.classes:
#      print "is class "+t+" external? "
#      print t.is_external(doap_spec)
      ''

  # work in progress.  
  def testFOAFusingDCasExternal(self):
    """FOAF using external vocabs"""
    foaf_spec = Vocab(dir=FOAFSNAPSHOTDIR, f=FOAFSNAPSHOT)
    foaf_spec.index()
    foaf_spec.uri = str(FOAF)
    for t in foaf_spec.terms:
      # print "is term "+t+" external? ", t.is_external(foaf_spec)
      ''

  def testniceName_1foafmyprop(self):
    """simple test of nicename for a known namespace (FOAF), unknown property"""
    foaf_spec = Vocab(dir=FOAFSNAPSHOTDIR, f=FOAFSNAPSHOT)
    u = 'http://xmlns.com/foaf/0.1/myprop'
    nn = foaf_spec.niceName(u)
    # print "nicename for ",u," is: ",nn
    self.failUnless(nn == 'foaf:myprop', "Didn't extract nicename. input is"+u+"output was"+nn)


  # we test behaviour for real vs fake properties, just in case...
  def testniceName_2foafhomepage(self):
    """simple test of nicename for a known namespace (FOAF), known property."""
    foaf_spec = Vocab(FOAFSNAPSHOTDIR,FOAFSNAPSHOT)
    foaf_spec.index()
    u = 'http://xmlns.com/foaf/0.1/homepage'
    nn = foaf_spec.niceName(u)
    # print "nicename for ",u," is: ",nn
    self.failUnless(nn == 'foaf:homepage', "Didn't extract nicename")

  def testniceName_3mystery(self):
    """simple test of nicename for an unknown namespace"""
    foaf_spec = Vocab(FOAFSNAPSHOTDIR,FOAFSNAPSHOT)
    foaf_spec.index()
    u = 'http:/example.com/mysteryns/myprop'
    nn = foaf_spec.niceName(u)
    # print "nicename for ",u," is: ",nn
    self.failUnless(nn == 'http:/example.com/mysteryns/:myprop', "Didn't extract verbose nicename")

  def testniceName_3baduri(self):
    """niceName should return same string if passed a non-URI (but log a warning?)"""
    foaf_spec = Vocab(FOAFSNAPSHOTDIR,FOAFSNAPSHOT)
    foaf_spec.index()
    u = 'thisisnotauri'
    nn = foaf_spec.niceName(u)
    #  print "nicename for ",u," is: ",nn
    self.failUnless(nn == u, "niceName didn't return same string when given a non-URI")

  def test_set_uri_in_constructor(self):
    """v = Vocab( uri=something ) can be used to set the Vocab's URI. """
    u = 'http://example.com/test_set_uri_in_constructor'
    foaf_spec = Vocab(FOAFSNAPSHOTDIR,FOAFSNAPSHOT,uri=u)
    foaf_spec.index()
    self.failUnless( foaf_spec.uri == u, "Vocab's URI was supposed to be "+u+" but was "+foaf_spec.uri)

  def test_set_bad_uri_in_constructor(self):
    """v = Vocab( uri=something ) can be used to set the Vocab's URI to a bad URI (but should warn). """
    u = 'notauri'
    foaf_spec = Vocab(FOAFSNAPSHOTDIR,FOAFSNAPSHOT,uri=u)
    foaf_spec.index()
    self.failUnless( foaf_spec.uri == u, "Vocab's URI was supposed to be "+u+" but was "+foaf_spec.uri)


  def test_getset_uri(self):
    """getting and setting a Vocab uri property"""
    foaf_spec = Vocab(FOAFSNAPSHOTDIR,FOAFSNAPSHOT,uri='http://xmlns.com/foaf/0.1/')
    foaf_spec.index()
    u = 'http://foaf.tv/example#'
    # print "a) foaf_spec.uri is: ", foaf_spec.uri 
    foaf_spec.uri = u
    # print "b) foaf_spec.uri is: ", foaf_spec.uri 
    # print
    self.failUnless( foaf_spec.uri == u, "Failed to change uri.")

  def test_ns_split(self):
    from libvocab import ns_split
    a,b = ns_split('http://example.com/foo/bar/fee')
    self.failUnless( a=='http://example.com/foo/bar/')
    self.failUnless( b=='fee') # is this a bad idiom? use AND in a single assertion instead?
 
  def test_lookup_Person(self):
    """find a term given it's uri"""
    foaf_spec = Vocab(dir=FOAFSNAPSHOTDIR,f=FOAFSNAPSHOT, uri='http://xmlns.com/foaf/0.1/') 
    foaf_spec.index()
    p = foaf_spec.lookup('http://xmlns.com/foaf/0.1/Person')
    # print "lookup for Person: ",p
    self.assertNotEqual(p.uri,  None, "Couldn't find person class in FOAF")

  def test_lookup_Wombat(self):
    """fail to a bogus term given it's uri"""
    foaf_spec = Vocab(dir=FOAFSNAPSHOTDIR,f=FOAFSNAPSHOT, uri='http://xmlns.com/foaf/0.1/') 
    foaf_spec.index()
    p = foaf_spec.lookup('http://xmlns.com/foaf/0.1/Wombat') # No Wombats in FOAF yet.
    self.assertEqual(p,  None, "lookup for Wombat should return None")

  def test_label_for_foaf_Person(self):
    """check we can get the label for foaf's Person class"""
    foaf_spec = Vocab(dir=FOAFSNAPSHOTDIR,f=FOAFSNAPSHOT, uri='http://xmlns.com/foaf/0.1/')
    foaf_spec.index()
    l = foaf_spec.lookup('http://xmlns.com/foaf/0.1/Person').label
    # print "Label for foaf Person is "+l
    self.assertEqual(l,"Person")

  def test_label_for_sioc_Community(self):
    """check we can get the label for sioc's Community class"""
    sioc_spec = Vocab(dir=SIOCSNAPSHOTDIR,f=SIOCSNAPSHOT, uri=SIOC)
    sioc_spec.index()
    l = sioc_spec.lookup(SIOC+'Community').label
    self.assertEqual(l,"Community")

  def test_label_for_foaf_workplaceHomepage(self):
    """check we can get the label for foaf's workplaceHomepage property"""
    foaf_spec = Vocab(dir=FOAFSNAPSHOTDIR, f=FOAFSNAPSHOT,uri='http://xmlns.com/foaf/0.1/')
    foaf_spec.index()
    l = foaf_spec.lookup('http://xmlns.com/foaf/0.1/workplaceHomepage').label
    # print "Label for foaf workplaceHomepage is "+l
    self.assertEqual(l,"workplace homepage")

  def test_status_for_foaf_Person(self):
    """check we can get the status for foaf's Person class"""
    foaf_spec = Vocab(dir=FOAFSNAPSHOTDIR,f=FOAFSNAPSHOT, uri='http://xmlns.com/foaf/0.1/')
    foaf_spec.index()
    s = foaf_spec.lookup('http://xmlns.com/foaf/0.1/Person').status
    self.assertEqual(s,"stable")

  # http://usefulinc.com/ns/doap#Repository
  def test_status_for_doap_Repository(self):
    """check we can get the computed 'unknown' status for doap's Repository class"""
    doap_spec = Vocab(dir=DOAPSNAPSHOTDIR,f=DOAPSNAPSHOT, uri='http://usefulinc.com/ns/doap#')
    doap_spec.index()
    s = doap_spec.lookup('http://usefulinc.com/ns/doap#Repository').status
    self.assertEqual(s,"unknown", "if vs:term_status isn't used, we set t.status to 'unknown'")

  def test_reindexing_not_fattening(self):
    "Indexing on construction and then a couple more times shouldn't affect property count."
    foaf_spec = Vocab(FOAFSNAPSHOTDIR,FOAFSNAPSHOT, uri = FOAF)
    foaf_spec.index()
    c = len(foaf_spec.properties)
    self.failUnless(c < 100 , "After indexing 3 times, foaf property count should still be < 100: "+str(c))

  def test_got_sioc(self):
    sioc_spec = Vocab(SIOCSNAPSHOTDIR,SIOCSNAPSHOT, uri = SIOC)
    sioc_spec.index()
    cr =  sioc_spec.lookup('http://rdfs.org/sioc/ns#creator_of')
    # print("Looked up creator_of in sioc. result: "+cr)
    # print("Looked up creator_of comment: "+cr.comment)
    # print "Sioc spec with comment has size: ", len(sioc_spec.properties)

  def testSIOCminprops(self):
    """Check we found at least 20 SIOC properties (which means matching OWL properties)"""
    sioc_spec = Vocab('examples/sioc/','sioc.rdf')
    sioc_spec.index()
    sioc_spec.uri = str(SIOC)
    c = len(sioc_spec.properties)
    self.failUnless(c > 20 , "SIOC has more than 20 properties. count was "+str(c))


  def testSIOCminprops_v2(self):
    """Check we found at least 10 SIOC properties."""
    sioc_spec = Vocab(dir='examples/sioc/',f='sioc.rdf', uri = SIOC)
    sioc_spec.index()
    c = len(sioc_spec.properties)
    self.failUnless(c > 10 , "SIOC has more than 10 properties. count was "+str(c))

  def testSIOCminprops_v3(self):
    """Check we found at least 5 SIOC properties."""
    # sioc_spec = Vocab(dir='examples/sioc/',f='sioc.rdf', uri = SIOC)
    sioc_spec = Vocab(dir=SIOCSNAPSHOTDIR,f=SIOCSNAPSHOT, uri = SIOC)
    sioc_spec.index()
    c = len(sioc_spec.properties)
    self.failUnless(c > 5 , "SIOC has more than 10 properties. count was "+str(c))

  def testSIOCmin_classes(self):
    """Check we found at least 5 SIOC classes."""
    sioc_spec = Vocab(dir=SIOCSNAPSHOTDIR,f=SIOCSNAPSHOT, uri = SIOC)
    sioc_spec.index()
    c = len(sioc_spec.classes)
    self.failUnless(c > 5 , "SIOC has more than 10 classes. count was "+str(c))

  def testFOAFmin_classes(self):
    """Check we found at least 5 FOAF classes."""
    foaf_spec = Vocab(dir=FOAFSNAPSHOTDIR,f=FOAFSNAPSHOT, uri = FOAF)
    foaf_spec.index()
    c = len(foaf_spec.classes)
    self.failUnless(c > 5 , "FOAF has more than 10 classes. count was "+str(c))

  def testHTMLazlistExists(self):
    """Check we have some kind of azlist. Note that this shouldn't really be HTML from Vocab API ultimately."""
    foaf_spec = Vocab(FOAFSNAPSHOTDIR, FOAFSNAPSHOT, uri = FOAF)
    foaf_spec.index()
    az = foaf_spec.azlist()   
#    print "AZ list is ", az
    self.assertNotEqual (az != None, "We should have an azlist.")

  def testOutputHTML(self):
    """Check HTML output formatter does something"""
    foaf_spec = Vocab(dir=FOAFSNAPSHOTDIR,f=FOAFSNAPSHOT, uri = FOAF)
    foaf_spec.index()
    page = VocabReport(foaf_spec)
    az = page.az()
    self.failUnless(az)


  def testGotRDFa(self):
    """Check HTML output formatter rdfa method returns some text"""
    foaf_spec = Vocab(dir=FOAFSNAPSHOTDIR,f=FOAFSNAPSHOT, uri = FOAF)
    foaf_spec.index()
    page = VocabReport(foaf_spec)
    rdfa = page.rdfa()
    self.failUnless(rdfa)

  def testTemplateLoader(self):
    """Check we can load a template file."""
    basedir = './examples/'
    temploc = 'template.html'
    f = open(basedir + temploc, "r")
    template = f.read()
    self.failUnless(template != None)


  def testTemplateLoader2(self):
    """Check we can load a template file thru constructors."""
    foaf_spec = Vocab(dir=FOAFSNAPSHOTDIR,f=FOAFSNAPSHOT, uri = FOAF)
    foaf_spec.index()
    page = VocabReport(foaf_spec, basedir='./examples/', temploc='template.html')
    tpl = page.template
    # print "Page template is: ", tpl
    self.failUnless(tpl != None)

  def testTemplateLoader3(self):
    """Check loaded template isn't default string."""
    foaf_spec = Vocab(FOAFSNAPSHOTDIR,FOAFSNAPSHOT, uri = FOAF)
    foaf_spec.index()
    page = VocabReport(foaf_spec, basedir='./examples/', temploc='template.html')
    tpl = page.template
    self.assertNotEqual(tpl, "no template loaded")

# TODO: check this fails appropriately: 
#  IOError: [Errno 2] No such file or directory: './examples/nonsuchfile.html'
#
#  def testTemplateLoader4(self):
#    """Check loaded template isn't default string when using bad filename."""
#    foaf_spec = Vocab(FOAFSNAPSHOT, uri = FOAF)
#    page = VocabReport(foaf_spec, basedir='./examples/', temploc='nonsuchfile.html')
#    tpl = page.template
#    self.assertNotEqual(tpl, "no template loaded")

  def testGenerateReport(self):
    """Use the template to generate our report page."""
    foaf_spec = Vocab(dir=FOAFSNAPSHOTDIR,f=FOAFSNAPSHOT, uri = FOAF)
    foaf_spec.index()
    page = VocabReport(foaf_spec, basedir='./examples/', temploc='template.html')
    tpl = page.template
    final = page.generate()
    rdfa = page.rdfa()
    self.assertNotEqual(final, "Nope!")


  def testSimpleReport(self):
    """Use the template to generate a simple test report in txt."""
    foaf_spec = Vocab(dir=FOAFSNAPSHOTDIR,f=FOAFSNAPSHOT, uri = FOAF)
    foaf_spec.index()
    page = VocabReport(foaf_spec, basedir='./examples/', temploc='template.html')
 
    simple = page.report()
    print "Simple report: ", simple
    self.assertNotEqual(simple, "Nope!")

def suite():
      suite = unittest.TestSuite()
      suite.addTest(unittest.makeSuite(testSpecgen))
      return suite

if __name__ == '__main__':
    print "Running tests..."
    suiteFew = unittest.TestSuite()

#   Add things we know should pass to a subset suite
#   (only skip things we have explained with a todo)
# 
    ##libby suiteFew.addTest(testSpecgen("testFOAFns"))
    ##libby suiteFew.addTest(testSpecgen("testSIOCns"))
    suiteFew.addTest(testSpecgen("testDOAPns"))
#    suiteFew.addTest(testSpecgen("testCanUseNonStrURI")) # todo: ensure .uri etc can't be non-str
    suiteFew.addTest(testSpecgen("testFOAFminprops"))
#    suiteFew.addTest(testSpecgen("testSIOCminprops")) # todo: improve .index() to read more OWL vocab
    suiteFew.addTest(testSpecgen("testSIOCmaxprops"))



#   run tests we expect to pass:
#    unittest.TextTestRunner(verbosity=2).run(suiteFew)

#   run tests that should eventually pass:
#    unittest.TextTestRunner(verbosity=2).run(suite())


# 
#  or we can run everything:
# http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html g = foafspec.graph 
#q= 'SELECT ?x ?l ?c ?type WHERE { ?x rdfs:label ?l . ?x rdfs:comment ?c . ?x a ?type . FILTER (?type = owl:ObjectProperty || ?type = owl:DatatypeProperty || ?type = rdf:Property || ?type = owl:FunctionalProperty || ?type = owl:InverseFunctionalProperty) } '
#query = Parse(q)
#relations = g.query(query, initNs=bindings)
#for (term, label, comment) in relations:
#        p = Property(term)
#        print "property: "+str(p) + "label: "+str(label)+ " comment: "+comment

if __name__ == '__main__':

    unittest.main()
