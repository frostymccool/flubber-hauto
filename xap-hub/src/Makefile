#**************************************************************************
#
#	Makefile
#
#	xap-hub makefile
#	
#	Copyright (c) 2012 Jose Luis Galindo <support@homected.com>
#	
#	This file is part of the HOMECTED project.
#	
#	HOMECTED is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; either version 2 of the License, or
#	(at your option) any later version.
#	
#	HOMECTED is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#	GNU General Public License for more details.
#	
#	You should have received a copy of the GNU General Public License
#	along with OPNODE; if not, write to the Free Software
#	Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#	
#	
#	Last changes:
#
#	10/04/12 by Jose Luis Galindo: first version.
#
#***************************************************************************/

XAP=hub

CC=gcc 
CFLAGS=-g -O2
LFLAGS=
INCLUDES=
LIBS=


xap-$(XAP): $(XAP).o
	$(CC) -o xap-$(XAP) $(LIBS) $(LFLAGS) $(XAP).o 
	mv xap-$(XAP) ../bin/xap-$(XAP)

$(XAP).o: $(XAP).c $(XAP).h
	$(CC) -c $(INCLUDES) $(CFLAGS) $(XAP).c 

clean:
	rm -f xap-$(XAP) *.o ../bin/xap-$(XAP)
