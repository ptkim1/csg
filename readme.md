# Coronavirus Seating Generator

This repository is for Paul Kim's MSCB 02-601 Placement Project

## Goal: 
Given a number of attendees, who may be subdivided into groups, and a fixed seating block, seat the attendees in a way to maximize the distance between individuals from different groups, while keeping groups together. 

## Organization
seating_generator.py will create a Seating object 
* with precisely specified dimensions and aisles
* randomly according to reasonable constraints otherwise
* seating is an object with an array representing the seating, and variables containing some meta-information

attendees_generator.py will take params from a seating object and generate groups of people, according to certain parameters (max and min number of people allowed in the seating)
* probably a list of ints, each int being the number of people in the group

Solver objects in solvers.py will take attendees and a Seating object, and return a seating arrangement

evaluator.py will take a seating arrangement and score it

visualizer.py will display the seating arrangement somehow

main.py will start the run, from either a json with parameters or user inputted parameters

TODO:

Comments and docstrings
