import evolution

name = "shape-genetics-starting"

in_path = "{}.jpg".format(name)
out_path = "{}_evolved.png".format(name)

steps = 30*1000
reevolutions = 20

# Letters
# gene_specs = {"mut_p": 30, "mut_r": 5, "mut_c": 50, "max_r": 200,
#              "init_r": 30, "mut_l": 0.3, "letters":"umbreon"}

# # Circles
# gene_specs = {"mut_p": 30, "mut_r": 3, "mut_c": 40, "max_r": 40, "init_r": 15}

# # Polygons
gene_specs = {"mut_p": 30, "mut_n": 0.1, "mut_c": 30, "init_r": 50, "max_n": 5}


evo_specs = {"pop_size": 50, "dna_len": 50, "kind": "polygon",
             "gene_switch_ratio": 0.2, "gene_mutation_ratio": 0.05,
             "property_mutation_ratio": 0.1, "combine_ratio": 0.1}

# Initial evolution
evolution.evolve_image(in_path, out_path, steps, gene_specs, evo_specs,
                       json_out=f"{name}_0.json")

# Reevolutions (offers breakpoints)
for k in range(0, reevolutions):
    evolution.continue_evolution(in_path, out_path, f"{name}_{k}.json", steps,
                                 json_out=f"{name}_{k+1}.json")

# Draw a big picture of final one
evolution.draw_dna_from_json(f"{name}_{reevolutions}.json",
                             f"{name}_big.png", 3000)
