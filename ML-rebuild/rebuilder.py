from sklearn import neighbors, ensemble, linear_model, naive_bayes
from sklearn import tree, gaussian_process, svm, neural_network


class rebuilder:

    def __init__(self):
        self.set_type("random", {})
        self.size = None
        self.truth = None
        return

    def rebuild(self):
        self.ml_model.fit(self.samples["where"], self.samples["what"])
        width, height = self.size
        world = [[x, y] for y in range(height) for x in range(width)]
        return self.ml_model.predict(world)

    def inform(self, samples, size):
        self.samples = samples
        self.size = size
        return

    def set_type(self, model, arguments):
        if model == "knn":
            self.__use_knn(arguments)
        elif model == "random":
            self.__use_randomforest(arguments)
        elif model == "rich":
            self.__use_richforest(arguments)
        elif model == "tree":
            self.__use_tree(arguments)
        elif model == "svm":
            self.__use_svm(arguments)
        elif model == "linear":
            self.__use_linear(arguments)
        elif model == "richlinear":
            self.__use_richlinear(arguments)
        elif model == "bayes":
            self.__use_bayes(arguments)
        elif model == "gauss":
            self.__use_gauss(arguments)
        elif model == "neural":
            self.__use_neural(arguments)
        else:
            print("defaulting to random forest")
            self.__use_randomforest(arguments)
        return

# -------MODEL SETTINGS----------------------------------------------------------

    def __use_knn(self, arguments):
        method = neighbors.KNeighborsRegressor
        self.ml_model = method()
        return

    def __use_randomforest(self, arguments):
        method = ensemble.RandomForestRegressor
        self.ml_model = method()
        return

    def __use_richforest(self, arguments):
        class RichForest:
            def __init__(self, guide):
                self.method = ensemble.RandomForestRegressor()
                self.guide = guide
                return

            def enrich(self, x, y, width, height):
                xx, yy = width - x, height - y
                basic = [x, y]
                diagonal = [x + y, x - y]
                multiplied = [x*y, xx*y, x*yy, xx*yy]
                return basic + diagonal + multiplied

            def fit(self, where, what):
                w, h = self.guide.size
                rich_where = [self.enrich(x, y, w, h) for [x, y] in where]
                self.method.fit(rich_where, what)
                return

            def predict(self, where):
                w, h = self.guide.size
                rich_where = [self.enrich(x, y, w, h) for [x, y] in where]
                return self.method.predict(rich_where)
        method = RichForest
        self.ml_model = method(self)
        return

    def __use_tree(self, arguments):
        method = tree.DecisionTreeRegressor
        self.ml_model = method()
        return

    def __use_svm(self, arguments):
        method = svm.SVR
        self.ml_model = method()
        return

    def __use_linear(self, arguments):
        method = linear_model.LinearRegression
        self.ml_model = method()
        return

    def __use_richlinear(self, arguments):
        class RichLinear:
            def __init__(self, guide):
                self.method = linear_model.Ridge()
                self.guide = guide
                return

            def enrich(self, x, y, width, height):
                basic = [x, y]
                multiplied = [x*x, y*y, x*y, x*x*y, x*y*y, x*x*y*y]
                return basic + multiplied

            def fit(self, where, what):
                w, h = self.guide.size
                rich_where = [self.enrich(x, y, w, h) for [x, y] in where]
                self.method.fit(rich_where, what)
                return

            def predict(self, where):
                w, h = self.guide.size
                rich_where = [self.enrich(x, y, w, h) for [x, y] in where]
                return self.method.predict(rich_where)
        method = RichLinear
        self.ml_model = method(self)
        return

    def __use_bayes(self, arguments):
        method = naive_bayes.GaussianNB
        self.ml_model = method()
        return

    def __use_gauss(self, arguments):
        method = gaussian_process.GaussianProcessRegressor
        self.ml_model = method()
        return

    def __use_neural(self, arguments):
        method = neural_network.MLPRegressor
        self.ml_model = method()
        return
