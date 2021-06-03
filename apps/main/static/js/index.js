// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        flag: true,
        search_name: '',
        search_cuisine: '',
        search_cooktime: '',
        ingredient1: '',
        ingredient2: '',
        ingredient3: '',
        ingredient4: '',
        ingredient5: '',
        results: [],
        total_results: 0,
        

        // Complete as you see fit.
    };


    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.new_search = function () {
        console.log(5555)
        axios.post(url_forms,
            {
                name: app.vue.search_name,
                cuisine: app.vue.search_cuisine,
                cooktime: app.vue.search_cooktime,
                ingredient1: app.vue.ingredient1,
                ingredient2: app.vue.ingredient2,
                ingredient3: app.vue.ingredient3,
                ingredient4: app.vue.ingredient4,
                ingredient5: app.vue.ingredient5,
             
            }).then(function (response) {
                

                axios.post(url_search, {
                    parameters: response.data.parameters
                }).then(function (response) {
                    app.vue.results = response.data.names;
                    app.vue.total_results = response.data.numResults;
                    if (app.vue.results) {
                        app.enumerate(app.vue.results)
                    }
                    app.set_flag(false);
                    //app.recipe_information(app.vue.total_results, app.vue.results);
                    // window.location.href = 'http://127.0.0.1:8000/main/recipe_information/' + app.vue.total_results+ '/'+ app.vue.results;
                    
                });
            });
    }
    app.recipe_information = function (n) {
        window.location.href = 'http://127.0.0.1:8000/main/recipe_information/' + n;
    }
    app.set_flag = function (b) {
        app.vue.flag = b;
    }
    
    // This contains all the methods.
    app.methods = {
        Search: app.new_search,
        recipe_information: app.recipe_information,
        set_flag: app.set_flag,
       
        
        // Complete as you see fit.
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
