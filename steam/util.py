import pickle
import urllib2
import xml.etree.ElementTree
import json
from BeautifulSoup import BeautifulSoup
from collections import defaultdict

# decorators!
def cachedreturn(n):
	def positional(fn):
		fn.lut = {}
		def wrapper(*args, **kwargs):
			try:
				return fn.lut[args[n]]
			except KeyError:
				fn.lut[args[n]] = fn(*args, **kwargs)
				return fn.lut[args[n]]
		return wrapper
	return positional

def runonce(fn):
	def wrapper(*args, **kwargs):
		try:
			return fn.ret_val
		except AttributeError:
			fn.ret_val = fn(*args, **kwargs)
			return fn.ret_val
	return wrapper

def deprecated(explanation):
	def deprecated_decorator(fn):
		def wrapper(*args, **kwargs):
			print 'DEPRECATED:', explanation
			fn(*args, **kwargs)
		return wrapper
	return deprecated_decorator



# fetchy things!
def _get_url(url):
	try:
		return urllib2.urlopen(url).read()
	except urllib2.HTTPError as e:
		print e, '\n', url
		raise e

def _strip_cdata(text):
	return text[9:-3].strip() if text[:9] == '<![CDATA[' else text

def _strip_unicode(text):
	return ''.join(x for x in text if ord(x) < 128)

# from http://stackoverflow.com/a/10077069
def _etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(_etree_to_dict, children):
            for k, v in dc.iteritems():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = _strip_cdata(text)
        else:
            d[t.tag] = _strip_cdata(text)
    return d

def _get_soup(url): return BeautifulSoup(_get_url(url))
def _get_json(url): return json.loads(_get_url(url))
def _get_xml(url):
	try:
		return _etree_to_dict(xml.etree.ElementTree.fromstring(_get_url(url)))
	except xml.etree.ElementTree.ParseError:
		print 'ERROR parsing', url
		return {}

# manually decorated versions, avoids fetching the same URL more than once
_get_url_cached = cachedreturn(0)(_get_url)
_get_xml_cached = cachedreturn(0)(_get_xml)
_get_soup_cached = cachedreturn(0)(_get_soup)
_get_json_cached = cachedreturn(0)(_get_json)




class MetaUniques(type):
	def __init__(cls, name, bases, dic):
		type.__init__(cls, name, bases, dic)
		cls.__instances = {}

	def _load(cls):
		try:
			with open('MetaUniques.{}.pickle'.format(cls.__name__), 'rb') as f:
				cls.__instances = pickle.load(f)
		except IOError:
			pass

	def _save(cls):
		with open('MetaUniques.{}.pickle'.format(cls.__name__), 'wb') as f:
			pickle.dump(cls.__instances, f)

	def __call__(cls, *args, **kwargs):
		if type(args[0]) is cls:
			# q&d copy (well more hardlink than copy) constructor
			return args[0]
		try:
			inst = cls.__instances[args[0]]
			inst._update(*args, **kwargs)
			return inst
		except KeyError:
			cls.__instances[args[0]] = super(MetaUniques, cls).__call__(*args, **kwargs)
			return cls.__instances[args[0]]

	def __getitem__(cls, key):
		return cls(key)

	def iterkeys(cls):
		return cls.__instances.iterkeys()

	def __iter__(cls):
		return cls.__instances.itervalues()
