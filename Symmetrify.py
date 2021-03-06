#MenuTitle: Symmetrify
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

'''
Symmetrifies the glyph shape.

S - creates point reflection (rotational symmetry)
T - creates horizontal reflection symmetry
C - creates vertical reflection symmetry
H - creates 2-axis symmetry (ie. all the above)

The buttons are available only as far as the node structure allows.

'''

from GlyphsApp import *

doc = Glyphs.currentDocument
font = doc.font
layers = doc.selectedLayers()
glyph = layers[0].parent

# print '______________________________________________________________'

from vanilla import Window, SquareButton

class SymmetrifyDialog( object ):

	def buttonCallback( self, sender ):
		self.button = sender.getTitle()
		self.w.close()

	def __init__( self, titles ):
		self.button = ''
		margin = 10
		size = 40
		self.w = Window( ( len( titles ) * ( margin + size ) + margin, 2 * margin + size ), "Symmetrify" )
		top = margin
		left = margin

		for title in titles:
			button = SquareButton( ( left, top, size, size ), title, callback = self.buttonCallback )
			setattr( self.w, title, button )
			left += size + margin

	def run( self ):
		self.w.open()
		while not self.button:
			pass
		return self.button


node_types = { 	GSLINE: 'o', GSCURVE: 'o', GSOFFCURVE: '.' }

for layer in layers:

	# center x and y
	cx = layer.bounds.origin.x + 0.5 * layer.bounds.size.width
	cy = layer.bounds.origin.y + 0.5 * layer.bounds.size.height
	# all the nodes, sorted by contour
	contours = [ [ node for node in path.nodes ] for path in layer.paths ]
	# node structures of the contours
	structures = [ [ node_types[node.type] for node in path.nodes ] for path in layer.paths ]

	# can it be rotated?
	allow_rotate = 0
	for c in range( len( contours ) ):
		if len( contours[c] ) % 2 == 1:
			break
		else:
			rotated_structure = structures[c][len(structures[c])/2:] + structures[c][:len(structures[c])/2]
			if structures[c] != rotated_structure:
				break
	else:
		allow_rotate = 1

	# can it be flipped?
	allow_flip = 0
	for c in range( len( contours ) ):
		allow_flip_temp = 0
		reversed_temp = structures[c][:]
		reversed_temp.reverse()
		for centre in range( len( contours[c] ) ):
			flipped_structure = reversed_temp[centre:] + reversed_temp[:centre]
			if structures[c] == flipped_structure:
				break
		else:
			break
	else:
		allow_flip = 1

	####################################################################################################

	def get_horipartner(c):
		for test in range(len(contours[c])):
			sum_temp = 0
			testpartner = test
			for n in range(len(contours[c])):
				sum_temp += abs(contours[c][n].x + contours[c][testpartner].x - 2*cx)
				sum_temp += abs(contours[c][n].y - contours[c][testpartner].y)*2
				if testpartner == 0:
					testpartner = len(contours[c])-1
				else:
					testpartner -= 1
			if test==0 or sum_temp < c_sum:
				c_sum = sum_temp
				result = test
		return result
	
	####################################################################################################

	def get_vertipartner(c):
		for test in range(len(contours[c])):
			sum_temp = 0
			testpartner = test
			for n in range(len(contours[c])):
				sum_temp += abs(contours[c][n].y + contours[c][testpartner].y - 2*cy)
				sum_temp += abs(contours[c][n].x - contours[c][testpartner].x)*2
				if testpartner == 0:
					testpartner = len(contours[c])-1
				else:
					testpartner -= 1
			if test==0 or sum_temp < c_sum:
				c_sum = sum_temp
				partner = test
				result = test
		return result
	
	####################################################################################################

	def horiflip():
		global cx, cy
		for c in range(len(contours)):
			if get_horipartner(c) % 2 == 0:
				cx = round(cx)
		for c in range(len(contours)):
			partner = get_horipartner(c)
			for n in range(len(contours[c])):
				contours[c][n].x	 = 0.50001*contours[c][n].x - 0.50001*contours[c][partner].x + cx
				contours[c][partner].x = 2*cx - contours[c][n].x
				contours[c][n].y	 = 0.5*contours[c][n].y + 0.5*contours[c][partner].y + 0.00001*(contours[c][n].x - 0.5*contours[c][partner].x)
				contours[c][partner].y = contours[c][n].y
				if partner == 0:
					partner = len(contours[c])-1
				else:
					partner -= 1
		# TODO: set advance width
		# g.SetMetrics( Point( cx*2, g.GetMetrics(m).y ), m )
	
	####################################################################################################
	
	def vertiflip():
		global cx, cy
		for c in range(len(contours)):
			if get_vertipartner(c) % 2 == 0:
				cy = round(cy)
		for c in range(len(contours)):
			partner = get_vertipartner(c)
			for n in range(len(contours[c])):
				contours[c][n].x	 = 0.5*contours[c][n].x + 0.5*contours[c][partner].x + 0.00001*(contours[c][n].y - 0.5*contours[c][partner].y)
				contours[c][partner].x = contours[c][n].x
				contours[c][n].y	 = 0.50001*contours[c][n].y - 0.50001*contours[c][partner].y + cy
				contours[c][partner].y = 2*cy - contours[c][n].y
				if partner == 0:
					partner = len(contours[c])-1
				else:
					partner -= 1
	
	####################################################################################################

	def bothflip():
		global cx, cy
		for c in range(len(contours)):
			if get_vertipartner(c) % 2 == 0:
				cy = round(cy)
			if get_horipartner(c) % 2 == 0:
				cx = round(cx)
		for c in range(len(contours)):
			partner_hflip  = get_horipartner(c)
			partner_rotate = len(contours[c])/2
			partner_vflip  = partner_hflip + partner_rotate
			if partner_vflip >= len(contours[c]):
				partner_vflip -= len(contours[c])
			for n in range(len(contours[c])+1/2):
				contours[c][n].x = 0.5001*(0.50001*contours[c][n].x - 0.50001*contours[c][partner_hflip ].x)   +   0.4999*(0.50001*contours[c][partner_vflip].x - 0.50001*contours[c][partner_rotate].x)  + cx + 0.000001*(contours[c][n].y - 0.5*contours[c][partner_vflip].y)
				contours[c][partner_hflip].x  = 2*cx - contours[c][n].x
				contours[c][partner_rotate].x = contours[c][partner_hflip].x
				contours[c][partner_vflip].x  = contours[c][n].x

				contours[c][n].y = 0.5001*(0.50001*contours[c][n].y - 0.50001*contours[c][partner_vflip ].y)   +   0.4999*(0.50001*contours[c][partner_hflip].y - 0.50001*contours[c][partner_rotate].y)  + cy + 0.000001*(contours[c][n].x - 0.5*contours[c][partner_hflip].x)
				contours[c][partner_vflip].y  = 2*cy - contours[c][n].y
				contours[c][partner_rotate].y = contours[c][partner_vflip].y
				contours[c][partner_hflip].y  = contours[c][n].y

				if partner_hflip == 0:
					partner_hflip = len(contours[c])-1
				else:
					partner_hflip -= 1

				if partner_vflip == 0:
					partner_vflip = len(contours[c])-1
				else:
					partner_vflip -= 1

				if partner_rotate == len(contours[c])-1:
					partner_rotate = 0
				else:
					partner_rotate += 1
		# TODO: set advance width
	
	####################################################################################################

	def rotate():
		global cx, cy
		for c in range(len(contours)):
			partner = len(contours[c])/2
			for n in range(partner):
				contours[c][n].x	 = 0.50001*contours[c][n].x - 0.50001*contours[c][partner].x + cx
				contours[c][partner].x = 2.0*cx - contours[c][n].x
				contours[c][n].y	 = 0.50001*contours[c][n].y - 0.50001*contours[c][partner].y + cy
				contours[c][partner].y = 2.0*cy - contours[c][n].y
				if partner == len(contours[c])-1:
					partner = 0
				else:
					partner += 1
		# TODO: set advance width
	
	####################################################################################################

	buttons = []
	
	if allow_rotate:
		buttons += [ 'S' ]
	if allow_flip:
		buttons += [ 'T', 'C' ]
		if 'S' in buttons:
			buttons += [ 'H' ]
	if buttons:
		dialog = SymmetrifyDialog( buttons )
		button = dialog.run()
		if button:
			font.disableUpdateInterface()
			glyph.beginUndo()
			if button == 'S':
				rotate()
			if button == 'T':
				horiflip()
			if button == 'C':
				vertiflip()
			if button == 'H':
				bothflip()
			glyph.endUndo()
			font.enableUpdateInterface()
	else:
		print 'No symmetrical structures in this glyph.'

