#! /usr/bin/env python

import curses,copy,os,os.path

class Board:
	def __init__(self,rows,cols):
		self.rows=rows
		self.cols=cols
		self.lowlimit=1
		self.highlimit=4
		self.spawnnum=3
		self.iters=0
		self.cells=[[0 for x in range(cols+2)] for y in range(rows+2)]
	def count_neighbours(self,row,col):
		count=0
		count-=self.cells[row][col]
		for i in range(row-1,row+2):
			for j in range(col-1,col+2):
				count+=self.cells[i][j]
		return count
	def toggle(self,row,col):
		if row<=self.rows and col <=self.cols:
			if self.cells[row][col]==0:
				self.cells[row][col]=1
			else:
				self.cells[row][col]=0
	def setcell(self,row,col,state):
                if row<=self.rows and col <=self.cols:
			self.cells[row][col]=state
			
def refresh_board(board):
	oldboard=copy.deepcopy(board)
	for row in range(1,oldboard.rows+1):
		for col in range(1,oldboard.cols+1):
			nb=oldboard.count_neighbours(row,col)
			if oldboard.cells[row][col]==1:
				#cell is alive
				if nb<=oldboard.lowlimit or nb>=oldboard.highlimit:
					board.setcell(row,col,0)
			else:
				#cell is dead
				if nb==oldboard.spawnnum:
					board.setcell(row,col,1)
	board.iters+=1

def refresh_screen(screen,board):
	height,width = screen.getmaxyx()

	if width>board.rows+1:
		width=board.rows+2
	if height>board.cols+1:
		height=board.cols+3

	for i in range(width):
		for j in range(height-1):
			if i==0:
				if j==0:
					screen.addstr(j,i," ")
				else:
					screen.addstr(j,i,str(j%10),curses.A_DIM)
			else:
				if j==0:
					screen.addstr(j,i,str(i%10),curses.A_DIM)
				else:
					screen.addstr(j,i," ",curses.color_pair(board.cells[i][j]))
	screen.addstr(height-1,width-1-len(str(board.iters)),str(board.iters))
	screen.refresh()

def parse_file(filename,board,x,y):
	file = open(filename, 'r')
	lines=file.readlines()
	row_offset=0
	for line in lines:
		if line[0]!="!":
			for col_offset in range(len(line)):
				if line[col_offset]==".":
					board.setcell(x+col_offset,y+row_offset,0)
				if line[col_offset]=="O":
					board.setcell(x+col_offset,y+row_offset,1)
			row_offset+=1

def main(screen):
	timeout=0
	curses.init_pair(1,curses.COLOR_GREEN,curses.COLOR_GREEN)

        screen.clear()
	screen.keypad(1)

	curses.nocbreak()
	curses.echo()
	#curses.curs_set(2)

	while False:
		screen.clear()
		screen.addstr(0,0,"Rows: ")
		try:
			rows=int(screen.getstr())
		except ValueError:
			continue
		else:
			break
	while False:
		screen.clear()
		screen.addstr(0,0,"Cols: ")
		try:
			cols=int(screen.getstr())
		except ValueError:
			continue
		else:
			break
	#just always use the whole screen...
	rows=180
	cols=60
	board=Board(rows,cols)

	refresh_screen(screen,board)

	height,width = screen.getmaxyx()

	curses.noecho()
	curses.cbreak()

	screen.addstr(height-1,0,"Space toggles squares. f reads from file. Return starts the game. q quits.")
	screen.move(1, 1)
	screen.refresh()
	
	while True: 
		event = screen.getch() 
		height,width = screen.getmaxyx()
		y, x = screen.getyx()
		if event == ord('q'): return
		if event == ord('\n'): break 
		if event == ord('f'):
			curses.echo()
			curses.nocbreak()
			screen.move(height-1,0)
			screen.clrtoeol()
			screen.addstr(height-1,0,"Enter filename: ")
			screen.refresh()
			filename = screen.getstr()
			if os.path.isfile(filename) and os.access(filename, os.R_OK):
				parse_file(filename,board,x,y)
				refresh_screen(screen,board)
			else:
				screen.move(height-1,0)
				screen.clrtoeol()
				screen.addstr(height-1,0,"File not found. Any key to continue.")
				screen.getch()
			curses.noecho()
			curses.cbreak()
			screen.move(height-1,0)
			screen.clrtoeol()
			screen.addstr(height-1,0,"Space toggles squares. f reads from file. Return starts the game. q quits.")
			screen.move(y, x)
			screen.refresh()
		if event == ord(' '):
			board.toggle(x,y)
			refresh_screen(screen,board)
			screen.move(y, x)
			screen.refresh()
		if event == curses.KEY_RIGHT:
			if x<board.rows and x < width-1:
				screen.move(y, x+1)
				screen.refresh()
		if event == curses.KEY_LEFT:
			if x>1:
				screen.move(y, x-1)
				screen.refresh()
		if event == curses.KEY_UP:
			if y>1:
				screen.move(y-1, x)
				screen.refresh()
		if event == curses.KEY_DOWN:
			if y<board.cols and y<height-2:
				screen.move(y+1, x)
				screen.refresh()

	screen.nodelay(1)
	screen.timeout(timeout)
	#curses.curs_set(0)
	screen.clear()
	screen.addstr(height-1,0,"Space pauses. q quits.")

	while True:
		event = screen.getch()
	#while key !=ord('q'):
		if event == ord(' '):
			while True:
				event2 = screen.getch()
				if event2 == ord(' '):
					break
				if event2==ord('q'):
					event=ord('q')
					break
		if event == ord('q'): break
		refresh_screen(screen,board)
		refresh_board(board)

curses.wrapper(main)
