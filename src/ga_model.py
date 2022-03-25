import copy
import random
import numpy as np
import src.music_functions
import src.evaluate

# most hard constraints will be translated to high penalty scores
# single-objective genetic algorithm & fitness function

class Population:
    
    def __init__(self):
        self.population = []
        
    def __len__(self):
        return len(self.population)
    
    def __iter__(self):
        return self.population.__iter__()
    
    def _extend(self, new_individuals):
        self.population.extend(new_individuals)
    
    def _append(self, new_individuals):
        self.population.append(new_individual)
    
    def _sort(self):
        assert len(self.population) > 0
        dct = {}
        x = 0
        for individual in self.population:
            dct[x] = individual.overall_fitness_score
        dct_sorted = dict(sorted(dct.items(), key=lambda item: item[1], reverse=True))
        population_sorted = [] * len(self.population)
        for k, v in dct_sorted:
            population_sorted.append(self.population[k])
        self.population = population_sorted
    
    def evaluate_population(self):
        for individual in self.population:
            calculate_overall_fitness(individual)
        
class Individual:
    
    def __init__(self, musical_input, x=None, c=None):
        self.rank = None
        self.musical_input = musical_input
        self.overall_fitness_score = 0
        self.gene_fitness_score = [0] * self.musical_input.melody_len
        self.individual_len = self.musical_input.melody_len
        self.x = x # decision variable for notes
        self.c = c # decision variable for chords
    
    def calculate_overall_fitness(self):
        self.overall_fitness_score = src.evaluate.evaluate_cost(self.x, self.c, self.musical_input.tonality, mode='')
    
    #def evaluate_gene_fitness(self):
        
    def update_gene_fitness(self, idx, score):
        self.gene_fitness_score[idx] += score
        #self.calculate_overall_fitness()
        self.overall_fitness_score += score
    
    def crossover_points(self):
        i, j = 0, 0
        score_list = copy.deepcopy(self.gene_fitness_score)
        for count in range(0, 2):
            max_value = max(score_list)
            max_idx = score_list.index(max_value)
            if count == 0:
                i = max_idx
                score_list.remove(max_value)
            else:
                j = max_idx
                score_list = []
                break
        return i, j
            

    '''
    to do: calculate fitness score of adjacent genes. window size=3?
    '''

class ga_model:
    
    def __init__(self, musical_input, chord_vocab, max_generation, population_size, hard_constraints, soft_constraints_weights, no_of_mutations, mutation_probability):
        self.musical_input = musical_input # an instance of the class MusicalWorkInput
        self.chord_vocab = chord_vocab
        self.chord_vocab_ext = []
        self.N = self.musical_input.melody_len
        self.K = self.musical_input.key
        self.x = np.zeros((4, self.N), dtype=int)
        self.c = np.zeros((self.N,))
        self.max_generation = max_generation
        self.population_size = population_size
        self.hard_constraints = hard_constraints
        self.soft_constraints_weights = soft_constraints_weights
        #self.constraint_encoding = encode_constraints(hard_constraints, soft_constraints_weights)
        self.no_of_mutations = no_of_mutations
        self.mutation_probability = mutation_probability
        self.voice_range_list = voice_range_bound()
        
    def voice_range_bound(self, lb = [19, 12, 5], ub = [38, 28, 26]):
        #voice_ranges = {1: (19, 38), 2: (12, 28), 3: (5, 26)}
        voice_range_list = np.zeros((3, self.N), dtype=int)
        for i in range(1,4):
            for j in range(self.N):
                voice_range_list[i,j] = (lb[i-1], ub[i-1])
        return voice_range_list
        
        hard_constraints = {'chord membership': self.hard_constraint_chord_membership, # also in initialize_harmony()
                            'first last chords': self.hard_constraint_first_last_chords,
                            'chord bass repetition': self.hard_constraint_chord_bass_repetition,
                            'adjacent bar chords': self.hard_constraint_adjacent_bar_chords,
                            'voice crossing': self.hard_constraint_voice_crossing,
                            'parallel movement': self.hard_constraint_parallel_movement,
                            'chord spacing': self.hard_constraint_chord_spacing}

        soft_constraints = {'chord progression': self.soft_constraint_chord_progression,
                            'chord repetition': self.soft_constraint_chord_repetition,
                            'chord bass repetition': self.soft_constraint_chord_bass_repetition,
                            'leap resolution': self.soft_constraint_leap_resolution,
                            'melodic movement': self.soft_constraint_melodic_movement,
                            'note repetition': self.soft_constraint_note_repetition,
                            'parallel movement': self.soft_constraint_parallel_movement,
                            'voice overlap': self.soft_constraint_voice_overlap,
                            'adjacent bar chords': self.soft_constraint_adjacent_bar_chords,
                            'chord spacing': self.soft_constraint_chord_spacing,
                            'distinct notes': self.soft_constraint_distinct_notes,
                            'voice crossing': self.soft_constraint_voice_crossing,
                            'voice range': self.soft_constraint_voice_range}
        
        for chord in self.chord_vocab:
            chord_vocab_ext.append(src.music_functions.extend_range(src.music_functions.transpose(chord.note_intervals, self.K)))
            
        for j in range(self.N):
            self.x[0,j] = self.musical_input.melody[j]
    
    def solve(self):
        population = initialize_population()
        for _ in range(max_generation):
            population.evaluate_population()
            population._sort() # sort the population in descending order of fitness score
            slicer = int(self.population_size * 0.1)
            if slicer % 2 != 0:
                slicer += 1
            new_population = Population()
            new_population.extend(population.population[:slicer])
            pool_size = self.population_size - slicer
            mating_pool = roulette_wheel_selection(population, pool_size)
            for x in range(0, len(mating_pool)-1, 2):
                parent_1, parent_2 = mating_pool[x], mating_pool[x+1]
                child_1 = crossover(parent_1, population)
                child_1, child_2 = mutation(child_1), mutation(child_2)
                new_population._apepnd(child_1)
                new_population._append(child_2)
            #new_population.evaluate_population()
            population = copy.deepcopy(new_population)
            new_population = None
        population._sort()
        best_solution = population.population[0]
        midi_array = [[]]
        for _ in range(3):
            midi_array.append([])
        sol_dict
        return best_solution
    
    def generate_individual(self):
        individual = Individual(self.musical_input, self.x)
        individual.c = initialize_chords(self.musical_input, self.chord_vocab, self.c)
        voice_range_limit = voice_range_bound()
        individual.x = initialize_harmony(self.musical_input, self.chord_vocab, self.chord_vocab_ext, self.c, self.x, voice_range_limit)
        individual.fitness_score = fitness_calculation(individual)
        return individual
            
    def initialize_population(self):
        population = Population()
        for _ in range(self.population_size):
            individual = generate_individual()
            population._append(individual)
        return population
    
    @staticmethod
    def initialize_chords(musical_input, chord_vocab, c):
        if musical_input.tonality == 'major':
            for chord in chord_vocab:
                if chord.name == 'I':
                    n = chord.index
                    break
            c[0] = n
            c[musical_input.melody_len - 1] = n
        elif musical_input.tonality == 'minor':
            n1 = []
            for chord in chord_vocab:
                if chord.name == 'i':
                    n = chord.index
                    n1.append(chord.index)
                elif chord.name == 'I':
                    n = chord.index
                    n1.append(chord.index)
            c[0] = n
            c[musical_input.melody_len - 1] = n1
        key = musical_input.key
        for idx in range(1, len(c)):
            chord_idx = random.randrange(len(chord_vocab))
            chord_name = chord_vocab[chord_idx].name
            c[idx] = chord
        return c
    
    @staticmethod
    def initialize_harmony(musical_input, chord_vocab, chord_vocab_ext, c, x, voice_range):
        for j in range(musical_input.melody_len):
            for i in range(1,4):
                for chord, chord_ext in zip(chord_vocab, chord_vocab_ext):
                    if c[j] == chord:
                        idx_slice = len(chord_ext) // 3
                        note_choice = []
                        rand_inversion = random.randrange(3)
                        if rand_inversion == 0: # root inversion
                            if i == 1:
                                note_choice.extend(chord_ext[idx_slice*2:])
                            elif i == 2:
                                note_choice.extend(chord_ext[idx_slice:idx_slice*2])
                            elif i == 3:
                                note_choice.extend(chord_ext[:idx_slice])
                        elif rand_inversion == 1: # first inversion
                            random_roll = random.random() # to cater for any voicing above the bass
                            if random_roll > 0.5:
                                if i == 1:
                                    note_choice.extend(chord_ext[:idx_slice])
                                elif i == 2:
                                    note_choice.extend(chord_ext[idx_slice*2:])
                            else:
                                if i == 1:
                                    note_choice.extend(chord_ext[idx_slice*2:])
                                elif i == 2:
                                    note_choice.extend(chord_ext[:idx_slice])
                            if i == 3:
                                note_choice.extend(chord_ext[idx_slice:idx_slice*2])
                        elif rand_inversion == 2: # second inversion
                            random_roll = random.random() # to cater for any voicing above the bass
                            if random_roll > 0.5:
                                if i == 1:
                                    note_choice.extend(chord_ext[:idx_slice])
                                elif i == 2:
                                    note_choice.extend(chord_ext[idx_slice:idx_slice*2])
                            else:
                                if i == 1:
                                    note_choice.extend(chord_ext[idx_slice:idx_slice*2])
                                elif i == 2:
                                    note_choice.extend(chord_ext[:idx_slice])
                            if i == 3:
                                note_choice.extend(chord_ext[idx_slice*2:])
                        filtered_note_choice = [note for note in note_choice if note >= voice_range[i][0] and note <= voice_range[i][1]]
                        x[i, j] = filtered_note_choice[random.randrange(len(filtered_note_choice))]
        return x
    
    def sum_of_fitness(self, population):
        score = 0
        for individual in population.population:
            score += individual.overall_fitness_score
        return score
    
    def roulette_wheel_selection(self, population, pool_size):
        # function assumes that population at input is already sorted
        total_score = sum_of_fitness(population)
        mating_pool = Population()
        for idx in range(pool_size):
            x = random.uniform(0, total_score)
            assert x < total_score
            partial_sum = 0
            for individual in population.population:
                partial_sum += individual.overall_fitness_score
                if partial_sum > x:
                    mating_pool._append(individual)
                    break
            if partial_sum <= x:
                mating_pool.append(population.population[-1])
        return mating_pool        
    
    def crossover(self, individual_1, mating_pool):
        # multi-point crossover
        i, j = crossover_points(individual_1)
        fitness_i, fitness_j = individual_1.gene_fitness_score[i], individual_1.gene_fitness_score[j]
        average_fitness = (fitness_i + fitness_j) / 2
        max_average, max_parent = 0, 0
        for individual in mating_pool:
            if individual != individual_1:
                i_1, j_1 = individual.gene_fitness_score[i], individual.gene_fitness_score[j]
                curr_average = (i_1 + j_1) / 2
                max_average = max(max_average, curr_average)
                if max_average == curr_average:
                    max_parent = individual
        child = copy.deepcopy(individual_1)
        child.x = individual_1.x[:i+1] + max_parent.x[i+1:j+1] + individual_1.x[j+1:]
        return child
    
    def mutation(self, individual, threshold):
        length = individual.individual_len
        no_of_mutations = self.no_of_mutations
        low_mutation_rate, high_mutation_rate = self.mutation_probability[0], self.mutation_probability[1]
        child = copy.deepcopy(individual)
        curr_mutations = 0
        for idx in range(child.individual_len):
            if curr_mutations >= no_of_mutations:
                break
            if child.gene_fitness_score[idx] >= threshold:
                mutation_rate = low_mutation_rate
            else:
                mutation_rate = high_mutation_rate
            if random.uniform(0,1) > mutation_rate:
                curr_mutations += 1
                c_i, x_i = child.c[idx], child.x[idx]
                chord_tones = chord_vocab_ext[c_i]
                for val in x_i:
                    chord_tones.remove(val)
                idx_slice = len(chord_tones) // 3
                rand_inversion = random.randrange(3)
                note_choice = []
                for i in range(1,4):
                    if rand_inversion == 0: # root inversion
                        if i == 1:
                            note_choice.extend(chord_tones[idx_slice*2:])
                        elif i == 2:
                            note_choice.extend(chord_tones[idx_slice:idx_slice*2])
                        elif i == 3:
                            note_choice.extend(chord_tones[:idx_slice])
                    elif rand_inversion == 1: # first inversion
                        random_roll = random.random() # to cater for any voicing above the bass
                        if random_roll > 0.5:
                            if i == 1:
                                note_choice.extend(chord_tones[:idx_slice])
                            elif i == 2:
                                note_choice.extend(chord_tones[idx_slice*2:])
                        else:
                            if i == 1:
                                note_choice.extend(chord_tones[idx_slice*2:])
                            elif i == 2:
                                note_choice.extend(chord_tones[:idx_slice])
                        if i == 3:
                            note_choice.extend(chord_tones[idx_slice:idx_slice*2])
                    elif rand_inversion == 2: # second inversion
                        random_roll = random.random() # to cater for any voicing above the bass
                        if random_roll > 0.5:
                            if i == 1:
                                note_choice.extend(chord_tones[:idx_slice])
                            elif i == 2:
                                note_choice.extend(chord_tones[idx_slice:idx_slice*2])
                        else:
                            if i == 1:
                                note_choice.extend(chord_tones[idx_slice:idx_slice*2])
                            elif i == 2:
                                note_choice.extend(chord_tones[:idx_slice])
                        if i == 3:
                            note_choice.extend(chord_tones[idx_slice*2:])
                    filtered_note_choice = [note for note in note_choice if note >= self.voice_range_list[i][0] and note <= self.voice_range_list[i][1]]
                child.x[i, idx] = filtered_note_choice[random.randrange(len(filtered_note_choice))]
        return child