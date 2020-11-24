import random
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageChops, ImageFont

tyGene = dict
tyDna = List[tyGene]
tyPop = List[Tuple[int, tyDna]]

# =============================================================================
# Just a quick template, since python lacks types


class GeneKind:

    def __init__(self, w, h, gene_specs):
        """ Sets the parameters of the gene creating class. """
        self.w, self.h, self.specs = w, h, gene_specs
        return

    def random_gene(self):
        """ Returns a random gene. """
        return {}

    def mutate_gene(self, ratio, gene: tyGene)-> tyGene:
        """ Returns a mutated version of a gene, does not change original. """
        return gene

    def combine_genes(self, gene1: tyGene, gene2: tyGene, ratio)-> tyGene:
        """ Returns a new gene, that is a combination of gene1 and gene2. """
        return {}

    def draw_gene(self, draw, gene: tyGene):
        """ Draws the gene onto the image. """
        return

    def recover_from_json(self, gene):
        """ Fixes the types after being read from json. """

    def upscale_gene(self, new_w, gene):
        """ Returns a new gene with upscaled parameters. """
        return gene


# =============================================================================

class CircleGene(GeneKind):

    def __init__(self, w, h, gene_specs):
        """ Sets the parameters of the gene creating class. """

        required = ["max_r", "init_r", "mut_p", "mut_r", "mut_c"]
        if not all([f in gene_specs.keys() for f in required]):
            raise KeyError(f"Circle genes require parameters {required}.")

        self.w, self.h, self.specs = w, h, gene_specs
        return

    def random_gene(self)-> tyGene:
        """ Returns a random gene. """
        point = random.randint(0, self.w), random.randint(0, self.h)
        r = self.specs["init_r"]
        color = tuple([random.randint(0, 256) for _ in range(4)])
        return {"point": point, "r": r, "color": color}

    def mutate_gene(self, ratio, gene: tyGene)-> tyGene:
        """ Returns a mutated version of a gene, does not change original. """
        mut_gene = gene.copy()

        # extract
        specs = self.specs
        mut_p, mut_r, mut_c = specs["mut_p"], specs["mut_r"], specs["mut_c"]

        # Position
        if random.random() < ratio:
            x, y = gene["point"]
            x_low, x_high = max(0, x - mut_p), min(self.w, x + mut_p)
            y_low, y_high = max(0, y - mut_p), min(self.h, y + mut_p)
            p = random.randint(x_low, x_high), random.randint(y_low, y_high)
            mut_gene["point"] = p

        # Size
        if random.random() < ratio:
            low = max(0, gene["r"] - mut_r)
            high = min(self.specs["max_r"], gene["r"] + mut_r)
            mut_gene["r"] = random.randint(low, high)

        # Color
        if random.random() < ratio:
            r, g, b, a = gene["color"]
            m_r = random.randint(max(0, r - mut_c), min(255, r + mut_c))
            m_g = random.randint(max(0, g - mut_c), min(255, g + mut_c))
            m_b = random.randint(max(0, b - mut_c), min(255, b + mut_c))
            m_a = random.randint(max(0, a - mut_c), min(255, a + mut_c))
            mut_gene["color"] = (m_r, m_g, m_b, m_a)

        return mut_gene

    def combine_genes(self, gene1: tyGene, gene2: tyGene, ratio)-> tyGene:
        """ Returns a new gene, that is a combination of gene1 and gene2. """
        def combiner(x1, x2):
            return (x1 if random.random() < ratio else x2)
        return {k: combiner(gene1[k], gene2[k]) for k in gene1.keys()}

    def draw_gene(self, draw, gene: tyGene):
        """ Draws the gene onto the image. """
        x, y = gene["point"]
        r = gene["r"]
        color = gene["color"]
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
        return

    def recover_from_json(self, gene):
        """ Fixes the types after being read from json. """
        fixed_gene = {}
        fixed_gene["point"] = (int(gene["point"][0]), int(gene["point"][1]))
        fixed_gene["r"] = int(gene["r"])
        fixed_gene["color"] = tuple(gene["color"])
        return fixed_gene

    def upscale_gene(self, new_w, gene):
        """ Returns a new gene with upscaled parameters. """
        f = new_w / self.w
        up_gene = gene.copy()
        up_gene["point"] = (int(gene["point"][0]*f), int(gene["point"][1]*f))
        up_gene["r"] = int(up_gene["r"]*f)
        return up_gene

# =============================================================================


class PolygonGene(GeneKind):

    def __init__(self, w, h, gene_specs):
        """ Sets the parameters of the gene creating class. """

        required = ["mut_p", "mut_c", "max_n", "mut_n", "init_r"]
        if not all([f in gene_specs.keys() for f in required]):
            raise KeyError(f"Polygon genes require parameters {required}.")

        self.w, self.h, self.specs = w, h, gene_specs
        self.specs["max_n"] = max(3, self.specs["max_n"])
        return

    def random_gene(self):
        """ Returns a random gene. """
        n = random.randint(3, self.specs["max_n"])
        r = self.specs["init_r"]

        # Limit points to a circle for better initial seeding
        (c_x, c_y) = (random.randint(0, self.w), random.randint(0, self.h))

        def acceptable(p):
            return ((c_x-p[0])**2 + (c_y-p[1])**2)**0.5 <= r

        def make_point():
            p = None
            while p is None or not acceptable(p):
                p = (random.randint(0, self.w), random.randint(0, self.h))
            return p

        points = [make_point() for _ in range(n)]
        color = tuple([random.randint(0, 256) for _ in range(4)])
        return {"points": points, "color": color}

    def mutate_gene(self, ratio, gene: tyGene)-> tyGene:
        """ Returns a mutated version of a gene, does not change original. """
        mut_gene = gene.copy()

        # extract
        specs = self.specs
        mut_p, mut_n, mut_c = specs["mut_p"], specs["mut_n"], specs["mut_c"]
        max_n = specs["max_n"]

        # Add or remove point
        if random.random() < ratio and random.random() < mut_n:
            points = mut_gene["points"].copy()
            add_point = random.random() < 0.5
            if add_point and len(points) < max_n:
                x, y = random.randint(0, self.w), random.randint(0, self.h)
                points.insert(random.randint(0, len(points)-1), (x, y))
            if not add_point and len(points) > 3:
                points.pop(random.randint(0, len(points)-1))

        # Position
        if random.random() < ratio:
            points = []
            for (x, y) in gene["points"]:
                x_low, x_high = max(0, x - mut_p), min(self.w, x + mut_p)
                y_low, y_high = max(0, y - mut_p), min(self.h, y + mut_p)
                p = random.randint(
                    x_low, x_high), random.randint(y_low, y_high)
                points.append(p)
            mut_gene["points"] = points

        # Color
        if random.random() < ratio:
            r, g, b, a = gene["color"]
            m_r = random.randint(max(0, r - mut_c), min(255, r + mut_c))
            m_g = random.randint(max(0, g - mut_c), min(255, g + mut_c))
            m_b = random.randint(max(0, b - mut_c), min(255, b + mut_c))
            m_a = random.randint(max(0, a - mut_c), min(255, a + mut_c))
            mut_gene["color"] = (m_r, m_g, m_b, m_a)

        return mut_gene

    def combine_genes(self, gene1: tyGene, gene2: tyGene, ratio)-> tyGene:
        """ Returns a new gene, that is a combination of gene1 and gene2. """
        def combiner(x1, x2):
            return (x1 if random.random() < ratio else x2)
        return {k: combiner(gene1[k], gene2[k]) for k in gene1.keys()}

    def draw_gene(self, draw, gene: tyGene):
        """ Draws the gene onto the image. """
        draw.polygon(gene["points"], fill=gene["color"])
        return

    def recover_from_json(self, gene):
        """ Fixes the types after being read from json. """
        fixed_gene = {}
        fixed_gene["points"] = [(p[0], p[1]) for p in gene["points"]]
        fixed_gene["color"] = tuple(gene["color"])
        return fixed_gene

    def upscale_gene(self, new_w, gene):
        """ Returns a new gene with upscaled parameters. """
        f = new_w / self.w
        up_gene = gene.copy()
        up_gene["points"] = [(p[0]*f, p[1]*f) for p in gene["points"]]
        return up_gene

# =============================================================================


class LetterGene(GeneKind):

    def __init__(self, w, h, gene_specs):
        """ Sets the parameters of the gene creating class. """

        required = ["init_r", "mut_p", "mut_r", "mut_l", "mut_c", "max_r"]
        if not all([f in gene_specs.keys() for f in required]):
            raise KeyError(f"Letter genes require parameters {required}.")

        self.w, self.h, self.specs = w, h, gene_specs

        # constants
        if gene_specs.get("letters", None):
            self.LETTERS = gene_specs["letters"]
        else:
            self.LETTERS = r"1234567890'+qwertzuiopšasdfghjklčž<yxcvbnm," \
                r".-!#$%&/()=?*QWERTZUIOPŠASDFGHJKLČŽ>YXCVBNM;:_~ˇ^°\|€@{}ß÷×¤"
        self.FONTMIN = 5
        self.FONTMAX = 500
        self.specs["max_r"] = min(self.FONTMAX, self.specs["max_r"])
        self.fonts = [
            ImageFont.truetype(font="arial.ttf", size=i) for i in range(
                self.FONTMIN, self.FONTMAX+1)]

        return

    def random_gene(self):
        """ Returns a random gene. """
        point = random.randint(-20, self.w), random.randint(-20, self.h)
        # Fix init_r to bounds
        r = max(self.FONTMIN, min(self.specs["max_r"], self.specs["init_r"]))
        color = tuple([random.randint(0, 256) for _ in range(4)])
        letter = random.choice(self.LETTERS)
        return {"point": point, "r": r, "color": color, "letter": letter}

    def mutate_gene(self, ratio, gene: tyGene)-> tyGene:
        """ Returns a mutated version of a gene, does not change original. """
        mut_gene = gene.copy()

        # extract
        specs = self.specs
        mut_p, mut_r = specs["mut_p"], specs["mut_r"]
        mut_c, mut_l = specs["mut_c"], specs["mut_l"]

        # Position
        if random.random() < ratio:
            x, y = gene["point"]
            x_low, x_high = max(-20, x - mut_p), min(self.w, x + mut_p)
            y_low, y_high = max(-20, y - mut_p), min(self.h, y + mut_p)
            p = random.randint(x_low, x_high), random.randint(y_low, y_high)
            mut_gene["point"] = p

        # Size
        if random.random() < ratio:
            low = max(self.FONTMIN, gene["r"] - mut_r)
            high = min(self.specs["init_r"], gene["r"] + mut_r)
            mut_gene["r"] = random.randint(low, high)

        # Color
        if random.random() < ratio:
            r, g, b, a = gene["color"]
            m_r = random.randint(max(0, r - mut_c), min(255, r + mut_c))
            m_g = random.randint(max(0, g - mut_c), min(255, g + mut_c))
            m_b = random.randint(max(0, b - mut_c), min(255, b + mut_c))
            m_a = random.randint(max(0, a - mut_c), min(255, a + mut_c))
            mut_gene["color"] = (m_r, m_g, m_b, m_a)

        # Letter
        if random.random() < ratio and random.random() < mut_l:
            mut_gene["letter"] = random.choice(self.LETTERS)

        return mut_gene

    def combine_genes(self, gene1: tyGene, gene2: tyGene, ratio)-> tyGene:
        """ Returns a new gene, that is a combination of gene1 and gene2. """
        def combiner(x1, x2):
            return (x1 if random.random() < ratio else x2)
        return {k: combiner(gene1[k], gene2[k]) for k in gene1.keys()}

    def draw_gene(self, draw, gene: tyGene):
        """ Draws the gene onto the image. """
        x, y = gene["point"]
        font = self.fonts[gene["r"] - self.FONTMIN]
        color = gene["color"]
        letter = gene["letter"]
        draw.text((x, y), letter, fill=color, anchor="rs", font=font)
        return

    def recover_from_json(self, gene):
        """ Fixes the types after being read from json. """
        fixed_gene = {}
        fixed_gene["point"] = (int(gene["point"][0]), int(gene["point"][1]))
        fixed_gene["r"] = int(gene["r"])
        fixed_gene["color"] = tuple(gene["color"])
        fixed_gene["letter"] = gene["letter"]
        return fixed_gene

    def upscale_gene(self, new_w, gene):
        """ Returns a new gene with upscaled parameters. """
        f = new_w / self.w
        up_gene = gene.copy()
        up_gene["point"] = (int(gene["point"][0]*f), int(gene["point"][1]*f))
        up_gene["r"] = max(self.FONTMIN, min(self.FONTMAX, int(gene["r"]*f)))
        return up_gene

# =============================================================================
# DNA functions


class DNA:

    def __init__(self, gene_tools: GeneKind, evo_specs):
        required = ["gene_mutation_ratio", "property_mutation_ratio",
                    "combine_ratio", "gene_switch_ratio"]
        if not all([f in evo_specs.keys() for f in required]):
            raise KeyError(f"DNA requires parameters {required}.")

        self.genes = gene_tools
        self.specs = evo_specs

    def random_dna(self, dna_len: int)-> tyDna:
        return [self.genes.random_gene() for _ in range(dna_len)]

    def combine_dna(self, dna1: tyDna, dna2: tyDna)-> tyDna:
        comb_ratio = self.specs["combine_ratio"]

        def combiner(g1, g2):
            if random.random() < comb_ratio:
                return self.genes.combine_genes(g1, g2, comb_ratio)
            else:
                return g1
        return [combiner(g1, g2) for g1, g2 in zip(dna1, dna2)]

    def mutate_dna(self, dna: tyDna) -> tyDna:
        mutation_ratio = self.specs["gene_mutation_ratio"]
        prop_ratio = self.specs["property_mutation_ratio"]
        switch_ratio = self.specs["gene_switch_ratio"]

        def mutator(gene):
            if random.random() < mutation_ratio:
                return self.genes.mutate_gene(prop_ratio, gene)
            else:
                return gene

        mut_dna = [mutator(gene) for gene in dna]

        if random.random() < switch_ratio:
            i = random.randint(0, len(mut_dna)-1)
            j = random.randint(0, len(mut_dna)-1)
            mut_dna[i], mut_dna[j] = mut_dna[j], mut_dna[i]

        return mut_dna

    def dna_to_image(self, dna: tyDna):
        # The first gene is the background
        if len(dna) < 1:
            raise Exception("DNA has to be at least 1 long!")

        background = dna[0].get("color", (0, 0, 0, 0))
        dna_img = Image.new("RGB", (self.genes.w, self.genes.h), background)
        draw = ImageDraw.Draw(dna_img, "RGBA")
        for gene in dna:
            self.genes.draw_gene(draw, gene)
        return dna_img

    def evaluate_dna(self, dna: tyDna, img)-> int:
        """Calculates the difference between the image and the DNA drawing."""
        def calculate_diff(img1, img2):
            diff_img = ImageChops.difference(img1, img2)
            total_diff = sum((x+y+z) for (x, y, z) in diff_img.getdata())
            return total_diff

        dna_img = self.dna_to_image(dna)
        return calculate_diff(img, dna_img)

    def recover_from_json(self, dna: tyDna)-> int:
        """Fixes the types after being read from json."""
        fixed_dna = [self.genes.recover_from_json(gene) for gene in dna]
        return fixed_dna

    def upscale_dna_and_self(self, new_w, dna):
        """ Returns a new dna with upscaled parameters. Also changes parameters
        of itself to new width. """
        upscaled_dna = [self.genes.upscale_gene(new_w, g) for g in dna]
        self.genes.h = int(self.genes.h * new_w / self.genes.w)
        self.genes.w = new_w
        return upscaled_dna
