import genetics
import random
import json
from typing import List, Tuple
from PIL import Image

tyGene = dict
tyDna = List[tyGene]
tyPop = List[Tuple[int, tyDna]]

# Serves for reporting during evolution
THIN_SEP = "-"*80
THICK_SEP = "="*80


def initial_population(dna_tools, dna_len: int, pop_size: int, img)-> tyPop:
    """ Generates a random initial population. """
    # generate dnas
    dnas = [dna_tools.random_dna(dna_len) for _ in range(pop_size)]
    # add scores
    pop = [(dna_tools.evaluate_dna(dna, img), dna) for dna in dnas]
    return pop


def population_from_dna(dna_tools, dna: tyDna, pop_size: int,
                        num_of_mutations: int, img)-> tyPop:
    """ Uses a dna to generate a population from it by mutating. """
    dnas = [dna]  # the original is always part of population
    # reseed population by mutating dna
    for _ in range(pop_size-1):
        mut_dna = dna_tools.mutate_dna(dna)
        for _ in range(num_of_mutations-1):
            mut_dna = dna_tools.mutate_dna(mut_dna)
        dnas.append(mut_dna)
    # add_scores
    pop = [(dna_tools.evaluate_dna(dna, img), dna) for dna in dnas]
    return pop


def evolve_pop_step(pop: tyPop, dna_tools, img)-> Tuple[tyPop, int]:
    """ Generates an offspring by combining two genes from the population and
    mutating it. The resulting element has to compete to earn a place in the
    population. Also returns the score of new element. """
    # combine
    _, dna1 = random.choice(pop)
    _, dna2 = random.choice(pop)
    mut_dna = dna_tools.combine_dna(dna1, dna2)

    # mutate
    mut_dna = dna_tools.mutate_dna(mut_dna)

    # compete
    score = dna_tools.evaluate_dna(mut_dna, img)
    competitor = random.randint(0, len(pop)-1)
    if score < pop[competitor][0]:
        pop[competitor] = (score, mut_dna)

    return pop, score


def evolve_pop(pop: tyPop, dna_tools, img, steps,
               steps_start=0, generate_steps=True, report=100000)-> tyPop:
    """ Evolves the population to fit the image [img] for [steps] iterations.
    If [generate_steps] is enabled, an image is saved whenever a 5% improvement
    is achieved. The current score is reported every [report] iterations, which
    is turned off by setting it to a negative number. """

    # For reporting purposes
    score, dna = min(pop, key=lambda p: p[0])

    # Draw initial one
    if generate_steps:
        dna_img = dna_tools.dna_to_image(dna)
        dna_img.save(f"ztep_{steps_start}.png")

    old_score = score  # used to report successful improvements of 5%
    for i in range(steps_start, steps_start+steps):
        pop, score = evolve_pop_step(pop, dna_tools, img)

        # Check if there was enough improvement to generate image
        if generate_steps and (score < old_score*0.95):
            old_score, dna = min(pop, key=lambda p: p[0])
            dna_img = dna_tools.dna_to_image(dna)
            dna_img.save("ztep_{}.png".format(i))

            if report > 0:
                pop_diff = max(pop, key=lambda p: p[0])[0] - score
                print(THIN_SEP)
                print(f"SUCCESS! Step : {i} | Score : {score} " +
                      f"| Population diff: {pop_diff}")

        elif report > 0 and i % report == 0:
            score, _ = min(pop, key=lambda p: p[0])
            pop_diff = max(pop, key=lambda p: p[0])[0] - score
            print(THIN_SEP)
            print(f"REPORT! Step : {i} | Score : {score}" +
                  f"| Population diff: {pop_diff}")

    return pop


def evolve_image(in_path, out_path, steps, gene_specs, evo_specs,
                 generate_steps=True, report=100000, json_out=None):

    img = Image.open(in_path)
    w, h = img.width, img.height

    required = ["kind", "dna_len", "pop_size"]
    if not all([f in evo_specs.keys() for f in required]):
        raise KeyError(f"Evolution specs require parameters {required}.")

    # initialize gene and dna tools
    kind = evo_specs["kind"]
    if kind == "polygon":
        gene_tools = genetics.PolygonGene(w, h, gene_specs)
    elif kind == "letter":
        gene_tools = genetics.LetterGene(w, h, gene_specs)
    else:
        gene_tools = genetics.CircleGene(w, h, gene_specs)

    dna_tools = genetics.DNA(gene_tools, evo_specs)

    # initialize population
    dna_len, pop_size = evo_specs["dna_len"], evo_specs["pop_size"]
    pop = initial_population(dna_tools, dna_len, pop_size, img)

    # evolve
    if report > 0:
        print(THICK_SEP)
        print(f"Starting evolution for {steps} steps!")
        print(THICK_SEP)
    pop = evolve_pop(pop, dna_tools, img, steps,
                     generate_steps=generate_steps, report=report)

    # save best one
    _, dna = min(pop, key=lambda p: p[0])
    dna_img = dna_tools.dna_to_image(dna)
    dna_img.save(out_path)

    # save best dna to json to allow continuation or upscaling
    if json_out:
        full_specs = {"width": w, "height": h, "kind": kind, "steps": steps,
                      "gene_specs": gene_specs, "evo_specs": evo_specs,
                      "dna": dna}
        with open(json_out, 'w') as jfile:
            jfile.write(json.dumps(full_specs))

    return


def continue_evolution(in_path, out_path, json_in, steps, reseed_mutations=5,
                       generate_steps=True, report=100000, json_out=None):
    img = Image.open(in_path)
    w, h = img.width, img.height

    with open(json_in, "r") as jfile:
        text = jfile.read()
        data = json.loads(text)

    old_steps = data["steps"]
    w, h = data["width"], data["height"]
    kind, gene_specs = data["kind"], data["gene_specs"]

    # initialize gene and dna tools
    if kind == "polygon":
        gene_tools = genetics.PolygonGene(w, h, gene_specs)
    elif kind == "letter":
        gene_tools = genetics.LetterGene(w, h, gene_specs)
    else:
        gene_tools = genetics.CircleGene(w, h, gene_specs)

    evo_specs = data["evo_specs"]
    dna_tools = genetics.DNA(gene_tools, evo_specs)

    # initialize population
    dna = dna_tools.recover_from_json(data["dna"])
    pop_size = evo_specs["pop_size"]
    pop = population_from_dna(dna_tools, dna, pop_size, reseed_mutations, img)

    # evolve
    if report > 0:
        print(THICK_SEP)
        print(f"Continuing evolution for {steps} steps!")
        print(THICK_SEP)
    pop = evolve_pop(pop, dna_tools, img, steps, steps_start=old_steps,
                     generate_steps=generate_steps, report=report)

    # save best one
    _, dna = min(pop, key=lambda p: p[0])
    dna_img = dna_tools.dna_to_image(dna)
    dna_img.save(out_path)

    if json_out:
        full_specs = {"width": w, "height": h, "kind": kind,
                      "steps": old_steps+steps, "gene_specs": gene_specs,
                      "evo_specs": evo_specs, "dna": dna}
        with open(json_out, 'w') as jfile:
            jfile.write(json.dumps(full_specs))

    return


def draw_dna_from_json(json_path, output_path, new_width=None):
    with open(json_path, "r") as jfile:
        text = jfile.read()
        data = json.loads(text)

    w, h = data["width"], data["height"]
    if new_width is None:
        new_width = w

    kind, gene_specs = data["kind"], data["gene_specs"]

    # initialize gene and dna tools
    if kind == "polygon":
        gene_tools = genetics.PolygonGene(w, h, gene_specs)
    elif kind == "letter":
        gene_tools = genetics.LetterGene(w, h, gene_specs)
    else:
        gene_tools = genetics.CircleGene(w, h, gene_specs)

    evo_specs = data["evo_specs"]
    dna_tools = genetics.DNA(gene_tools, evo_specs)

    dna = dna_tools.recover_from_json(data["dna"])

    # also changes tools!
    dna = dna_tools.upscale_dna_and_self(new_width, dna)

    dna_img = dna_tools.dna_to_image(dna)
    dna_img.save(output_path)
