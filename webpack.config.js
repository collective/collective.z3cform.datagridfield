process.traceDeprecation = true;
const package_json = require("./package.json");
const path = require("path");
const patternslib_config = require("@patternslib/patternslib/webpack/webpack.config");
const mf_config = require("@patternslib/patternslib/webpack/webpack.mf");

module.exports = async (env, argv) => {
    let config = {
        entry: {
            "datagridfield.min": path.resolve(__dirname, "resources/datagridfield-config"),
        },
        optimization: {
            splitChunks: {
                cacheGroups: {
                    tinymce: {
                        name: "tinymce",
                        test: /[\\/]node_modules[\\/]tinymce.*[\\/]/,
                        chunks: "all",
                    },
                    select2: {
                        name: "select2",
                        test: /[\\/]node_modules[\\/]select2.*[\\/]/,
                        chunks: "all",
                    },
                },
            },
        },
    };

    config = patternslib_config(env, argv, config, ["mockup"]);
    config.output.path = path.resolve(__dirname, "src/collective/z3cform/datagridfield/static");

    config.plugins.push(
        mf_config({
            filename: "datagridfield-remote.min.js",
            package_json: package_json,
            remote_entry: config.entry["datagridfield.min"],
        })
    );

    if (process.env.NODE_ENV === "development") {
        config.devServer.port = "8011";
        config.devServer.static.directory = `${__dirname}/resources`;
    }

    return config;
};
