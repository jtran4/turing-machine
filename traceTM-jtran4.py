#!/usr/bin/env python3
import sys
import os
import time
import csv
from tqdm import tqdm
from collections import deque

# Tape class represents the state of the Turing machine tape
class Tape(object):
    def __init__(self, state, left = [], head = '_', right = []):
        self.state = state
        self.left = left
        self.head = head
        self.right = right

    def __str__(self):
        return ''.join(self.left) + ',' + self.state + ',' + self.head + ',' + ''.join(self.right)

# NTM class represents the Non-deterministic Turing Machine
class NTM(object):
    def __init__(self, file):
        self.input_file = file
        self.T = {} # Transition rules
        with open(self.input_file) as file:
            for index, line in tqdm(enumerate(file), desc='Reading TM file...'):
                # Parsing the TM configuration file
                if index == 0:
                    self.name = line.rstrip().split(',')[0]
                elif index == 1:
                    self.states = list(filter(None, line.rstrip().split(',')))
                elif index == 2:
                    self.sigma = list(filter(None, line.rstrip().split(',')))
                elif index == 3:
                    self.gamma = list(filter(None, line.rstrip().split(',')))
                elif index == 4:
                    self.start = line.rstrip().split(',')[0]
                elif index == 5:
                    self.accept = list(filter(None, line.rstrip().split(',')))
                elif index == 6:
                    self.reject = line.rstrip().split(',')[0]
                else:
                    self.read_transition(line.rstrip())

    # Read TM machine transitions from a line in the configuration file
    def read_transition(self, transition):
        transition = transition.split(',')
        if (len(transition) == 3):
            curr, input_char, next = transition[0:3]
            write_char = input_char
            direction = 'R'
        else:
            curr, input_char, next, write_char, direction = transition[0:5]

        # Update transition rules dictionary
        if curr not in self.T:
            self.T[curr] = {}
        if input_char not in self.T[curr]:
            self.T[curr][input_char] = []
        self.T[curr][input_char].append((next, write_char, direction))

    # Get the next possible transitions from the current tape configuration
    def get_transition(self, tape):
        curr_state = tape.state
        head = tape.head

        # If there is no transition, return None
        if head not in self.T[curr_state]:
            return None
        else:
            new_tapes = []
            for transition in self.T[curr_state][head]:
                next, replace_char, direction = transition
                # Replace current head
                head = replace_char
                left = tape.left
                right = tape.right

                # Get direction and update the tape
                if (direction == 'R'):
                    if len(tape.right) == 0:
                        right = ['_']
                    new_tape = Tape(state=next, left=left+[head], head=right[0], right=right[1:])

                else:
                    if len(tape.left) == 0:
                        left = ['_']
                    new_tape = Tape(state=next, left=left[:-1], head=left[-1], right=[head]+right)

                new_tapes.append(new_tape)
            return new_tapes

    # Trace the machine's execution using BFS
    def trace(self, string, max_steps, output_file):
        string_list = list(string)
        tape = Tape(state = self.start, head = string_list[0], right = string_list[1:])
        queue = deque([(tape,0, [tape])])
        visited = {}
        steps = 0
        accept = False
        while len(queue) > 0 and steps < max_steps:
            curr, level, path = queue.popleft()    

            # Keep track with the depth of the tree
            if level not in visited:
                visited[level] = []

            visited[level].append(tape)
            
            # Check if the current state is an accept state
            if (curr.state in self.accept):
                accept = True
                break

            if (curr.state in self.reject):
                continue
            
            # Get next transitions
            next = self.get_transition(curr)

            # If there's no next transition, move to the next state
            if next == None:
                continue
            else:
                for tape in next:
                    queue.append((tape, level+1, path+[tape]))
            steps += 1

        # Print and write results to the output file
        print(f'Depth of the tree of configurations: {max(visited.keys())}.')
        output_file.write(f'Depth of the tree of configurations: {max(visited.keys())}.\n')

        print(f'Total transitions: {steps}.')
        output_file.write(f'Total transitions: {steps}.\n')

        if (accept == True):
            print(f'String {string} accepted in {level} transitions.')
            output_file.write(f'String {string} accepted in {level} transitions. \n')
            for tape in path:
                print(tape)
                output_file.write(f'{tape}\n')

        else:
            if steps < max_steps:
                print(f'String {string} rejected in {max(visited.keys())} transitions.')
                output_file.write(f'String {string} rejected in {max(visited.keys())} transitions.\n')

            else:
                print(f'Execution stopped after {max_steps} max steps limit')
                output_file.write(f'Execution stopped after {max_steps} max steps limit.\n')
        
    
def main():
    # Get input file name from the user
    file = input('Enter TM file name: ')
    machine = NTM(file)

    # If the output file already exists, remove it
    file_name = machine.name.replace(' ', '')
    if os.path.exists(file_name+'-output.txt'):
        os.remove(file_name+'-output.txt')

    # Create and open the output file for writing
    output_file = open(file_name+'-output.txt', 'a')
    output_file.write(f'Name of the machine: {machine.name}.\n\n')
    while (True): 
        # Get input string or end input
        input_string = input('Enter input string or endinput: ')
        if input_string == 'endinput':
            break

        # Get maximum steps from the user
        max_steps = int(input('Enter max steps: '))
    
        print()
        print(f'Name of the machine: {machine.name}')
        print(f'Initial input string: {input_string}')
        output_file.write(f'Initial input string: {input_string}\n')

        # Trace the machine's execution
        machine.trace(input_string, max_steps, output_file)
        print()
        output_file.write('\n')
    
    # Close the output file 
    output_file.close()
  

if __name__ == '__main__':
    main()