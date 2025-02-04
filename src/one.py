#! /usr/bin/env python

import argparse
import importlib
import numpy

import twixt

parser = argparse.ArgumentParser(description='One twixt position.')
parser.add_argument('--mark', type=str)
parser.add_argument('--moves', '-m', type=str)
parser.add_argument('--check_draw', '-D', action='store_true')
parser.add_argument('--display', '-d', action='store_true')
parser.add_argument('--nneval', type=str)
parser.add_argument('--thinker', '-t', type=str)
parser.add_argument('--think_report', '-T', action='store_true')
parser.add_argument('--show_game_state', '-G', action='store_true')
parser.add_argument('-r', '--resource', type=str, action='append')
args = parser.parse_args()

if args.resource:
    resources = {r.name: r for r in [twixt.get_resource(thing) for thing in args.resource]}
else:
    resources = dict()

game = twixt.Game()

possible_moves = []
thinker_moves = []

if args.moves:
    for m in args.moves.split(','):
	game.play(m)

if args.nneval:
    import naf
    import nneval
    import random
    ROT = random.randint(0,3)
    ne = nneval.NNEvaluater(args.nneval)
    nips = naf.NetInputs(game)
    nips.rotate(ROT)
    pw, ml = ne.eval_one(nips)
    ml = naf.rotate_policy_array(ml[0,:], ROT)
    print "pwin=",pw

    LM = naf.legal_move_policy_array(game)
    LMnz = LM.nonzero()
    max_ml = ml[LMnz].max()
    el = numpy.exp(ml - max_ml)
    divisor = el[LMnz].sum()
    P = el / divisor
    # print P
    P[(1-LM).nonzero()] = 0
    inds = numpy.argsort(P)
    for idx, i in enumerate(reversed(inds[-40:])):
        coord = naf.policy_index_point(game, i)
        possible_moves.append(coord)
        if idx<10:
            print "%3s %6.2f" % (str(coord), P[i]*100.0)

    #import mpui
    #mpui.show_game_with_p(game, P)

if args.thinker:
    thinker = twixt.get_thinker(args.thinker, resources)
    tup = thinker.pick_move(game)
    if type(tup) == tuple:
	m, n = thinker.pick_move(game)
    else :
	m = tup

    # if m != "resign":
        # game.play(m)

    if args.think_report:
        _,rep = thinker.report.split("=")
        for m in rep.split(","):
            thinker_moves.append(twixt.Point(m))
	print thinker.report

if args.show_game_state:
    print "currently",game.COLOR_NAME[game.turn],"to play"
    if game.is_winning(game.BLACK):
	print "Black won"
    elif game.is_winning(game.WHITE):
	print "White won"
    else:
	count = 0
	if not game.can_win(game.BLACK):
	    print "Black cannot win"
	    count += 1
	if not game.can_win(game.WHITE):
	    print "White cannot win"
	    count += 1
	if count == 0:
	    print "Normal game state"
	elif count == 2:
	    print "Game Drawn"


if args.display:
    import ui
    w = ui.TwixtBoardWindow()
    
    w.draw_dummy(possible_moves)
    
    turn = game.turn
    if args.thinker:
        for m in thinker_moves:
            game.play(str(m))
            
    w.set_game(game)
    
    if args.mark:
        marks = []
        for m in args.mark.split(','):
            marks.append(twixt.Point(m))
	w.draw_dummy(marks, True);
        
    if args.thinker:
        w.draw_steps(thinker_moves, turn);
        
    w.win.getMouse()

if args.check_draw:
    if game.just_won():
        winner = 1 - game.turn
        print game.COLOR_NAME[winner]
    else:
        bcw = game.can_win(game.BLACK)
        wcw = game.can_win(game.WHITE)
        if wcw and bcw:
            print "live"
        elif wcw:
            print "wcw"
        elif bcw:
            print "bcw"
        else:
            print "draw"


