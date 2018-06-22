%
% Author: Peter Schüller (2014)
%

#const xmax=20.
#const ymax=20.

xcoo(1..xmax).
ycoo(1..ymax).

field(f(X,Y)) :- xcoo(X), ycoo(Y).

exit(f(1,2)).
entry(f(xmax,8)).

%%%

{ wall(F) } :- field(F).

:- wall(F), exit(F).
:- wall(F), entry(F).

%%%

%text(F,5) :- reachable(F).

border(f(1,Y)) :- ycoo(Y).
border(f(xmax,Y)) :- ycoo(Y).
border(f(X,1)) :- xcoo(X).
border(f(X,ymax)) :- xcoo(X).

%mark(F) :- border(F).
wall(F) :- border(F), not exit(F), not entry(F).

%%%

yadjacent(f(X,Y),f(X,Y+1)) :- xcoo(X), ycoo(Y), ycoo(Y+1).
xadjacent(f(X,Y),f(X+1,Y)) :- xcoo(X), ycoo(Y), xcoo(X+1).
yadjacent(A,B) :- yadjacent(B,A).
xadjacent(A,B) :- xadjacent(B,A).

adjacent(A,B) :- xadjacent(A,B).
adjacent(A,B) :- yadjacent(A,B).

:- field(A), not wall(A), { wall(B) : adjacent(A,B) } 0.

%%%

% A B
% C D
square(A,B,C,D) :- xadjacent(A,B), yadjacent(A,C), yadjacent(B,D), xadjacent(C,D).
:- square(A,B,C,D), wall(A), wall(D), not wall(C), not wall(B).
%:- square(A,B,C,D), { wall(A) ; wall(D); wall(C); wall(B) } 0.

%:- square(A,B,C,D), not border(A), not border(D), not 1 { wall(A) ; wall(B) ; wall(C) ; wall(D) } 3.

:- square(A,B,C,D),
   wall(A) , wall(B) , wall(C) , wall(D).

:- wall(A), not 1 { wall(B):adjacent(A,B) }.

%%%

reachable(F) :- exit(F).
reachable(G) :- reachable(F), adjacent(F,G), not wall(G).

:- field(F), not wall(F), not reachable(F).
mark(F) :- reachable(F).
%:- exit(F), not reachable(F).


