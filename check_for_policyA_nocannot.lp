%%%%% POLICY A %%%%%%%%%
% 11 Oct
%same as check_for_policyA_old_quad_v2.lp but no quad


#const n = 4.
#const time = 3.
#const maxObs=10.

row(0..n-1).
column(0..n-1).

time(0..time).
timea(0..time-1).


dist(1..n-1).

inRegion(0..(n/2)-1,0..(n/2)-1,nw).
inRegion(0..(n/2)-1,(n/2)..n-1,ne).
inRegion((n/2)..n-1,0..(n/2)-1,sw).
inRegion((n/2)..n-1,(n/2)..n-1,se).

dir(west, 0, -1).
dir(east,  0, 1).
dir(north, -1,0).
dir(south, 1, 0).

robotAt(0,0,0).

%%%

1{target(X,Y,X,Y1,east,T): robotAt(X,Y,T), Y1>Y, inRegion(X,Y1,R1), column(Y1);
  target(X,Y,X,Y1,west,T): robotAt(X,Y,T), Y1<Y, inRegion(X,Y1,R1), column(Y1);
  target(X,Y,X1,Y,south,T): robotAt(X,Y,T), X1>X, inRegion(X1,Y,R1), row(X1);
  target(X,Y,X1,Y,north,T): robotAt(X,Y,T), X1<X, inRegion(X1,Y,R1), row(X1)}1 :- agentAt(R,T), goRegion(R,R1,T),timea(T).


%if farthest point in region, should be in same row or same column
1{target(X,Y,X1,Y,south,T): robotAt(X,Y,T), X1>X, inRegion(X1,Y,R1), row(X1); 
  target(X,Y,X1,Y,north,T): robotAt(X,Y,T), X1<X, inRegion(X1,Y,R1), row(X1); 
  target(X,Y,X,Y1,east,T): robotAt(X,Y,T), Y1>Y, inRegion(X,Y1,R1), column(Y1); 
  target(X,Y,X,Y1,west,T): robotAt(X,Y,T), Y1<Y, inRegion(X,Y1,R1), column(Y1)}1 :- agentAt(R,T), stayInRegion(R1,T),timea(T).

%
robotAt(X1,Y1,T+1) :- target(X,Y,X1,Y1,DIR,T),timea(T).
%
farthestOnNorth(X,Y,X1,T) :- target(X,Y,X1,Y,north,T).
farthestOnSouth(X,Y,X1,T) :- target(X,Y,X1,Y,south,T).
farthestOnEast(X,Y,Y1,T) :- target(X,Y,X,Y1,east,T).
farthestOnWest(X,Y,Y1,T) :- target(X,Y,X,Y1,west,T).
%
obstacleAt(X1-1,Y,T) :- farthestOnNorth(X,Y,X1,T), X1>0.
obstacleAt(X1+1,Y,T) :- farthestOnSouth(X,Y,X1,T), X1<n-1.
obstacleAt(X,Y1-1,T) :- farthestOnWest(X,Y,Y1,T), Y1>0.
obstacleAt(X,Y1+1,T) :- farthestOnEast(X,Y,Y1,T), Y1<n-1.
%
obstacleAt(X,Y,T+1):-obstacleAt(X,Y,T),timea(T).
%
%CONSISTENCY CONSTRAINTS
% (1)
%if there is an obstacle at a cell, then the robot shouldn't be at that cell
:- obstacleAt(X,Y,T), robotAt(X,Y,T).
% (2)
%cannot determine a farthest point towards a direction, if an obstacle was determined in between
:- farthestOnEast(X,YY,YY1,T),obstacleAt(X,Y,T),YY<Y,YY1>=Y,timea(T).
:- farthestOnWest(X,YY,YY1,T),obstacleAt(X,Y,T),YY>Y,YY1<=Y,timea(T).
:- farthestOnSouth(XX,Y,XX1,T),obstacleAt(X,Y,T),XX<X,XX1>=X,timea(T).
:- farthestOnNorth(XX,Y,XX1,T),obstacleAt(X,Y,T),XX>X,XX1<=X,timea(T).

%
%BEHAVIOUR CONSTRAINTS
%
targetDist(X,Y,D,T) :- target(X,Y,X1,Y1,DIR,T), dir(DIR,I,J), D=|X-X1|+|Y-Y1|, dist(D).
%
% (3)
%can not determine different distances from the same point at different times
:- targetDist(X,Y,D,T), targetDist(X,Y,DD,T1), D!=DD, T1>T,timea(T),timea(T1). 
% (4)
%if a farthest point X,Y1 with distance D was reached, the next farthest point from X,Y1 shouldnt have a distance less than D
targetDist_(D,T) :- targetDist(_,_,D,T).
:- targetDist_(D,T), targetDist_(D1,T1), T1=T+1, D1<D.

% (5)
%if a target is determined in the same direction, it should be the same as before
:- target(X,YY,X,YY1,east,T1),target(X,Y,X,Y1,east,T),YY<=Y1,YY1<Y1,YY1>=Y,T1>T,timea(T),timea(T1).
:- target(X,YY,X,YY1,west,T1),target(X,Y,X,Y1,west,T),YY>=Y1,YY1>Y1,YY1<=Y,T1>T,timea(T),timea(T1).
:- target(XX,Y,XX1,Y,south,T1),target(X,Y,X1,Y,south,T),XX<=X1,XX1<X1,XX1>=X,T1>T,timea(T),timea(T1).
:- target(XX,Y,XX1,Y,north,T1),target(X,Y,X1,Y,north,T),XX>=X1,XX1>X1,XX1<=X,T1>T,timea(T),timea(T1).


obsAt(X,Y) :- obstacleAt(X,Y,T).
:- maxObs+1 {obsAt(X,Y):row(X),column(Y)}.

#show.
#show robotAt/3.
#show row/1.
#show column/1.
%#show farthestOnEast/4.
%#show farthestOnWest/4.
%#show farthestOnSouth/4.
%#show farthestOnNorth/4.
#show target/6.
#show targetDist/4.
#show obstacleAt/3.
