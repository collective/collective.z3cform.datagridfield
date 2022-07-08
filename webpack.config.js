process.traceDeprecation = true;
const mf_config = require("@patternslib/dev/webpack/webpack.mf");
const path = require("path");
const package_json = require("./package.json");
const package_json_mockup = require("@plone/mockup/package.json");
const patternslib_config = require("@patternslib/dev/webpack/webpack.config.js");

module.exports = async (env, argv) => {
    let config = {
        entry: {
            "datagridfield.min": path.resolve(__dirname, "resources/datagridfield-config"),
        },
    };

    config = patternslib_config(env, argv, config, ["@plone/mockup"]);
    config.output.path = path.resolve(__dirname, "src/collective/z3cform/datagridfield/static");

    config.plugins.push(
        mf_config({
            name: "datagridfield",
            filename: "datagridfield-remote.min.js",
            remote_entry: config.entry["datagridfield.min"],
            dependencies: {
                ...package_json_mockup.dependencies,
                ...package_json.dependencies,
            },
        })
    );

    if (process.env.NODE_ENV === "development") {
        config.devServer.port = "8011";
        config.devServer.static.directory = `${__dirname}/resources`;
    }

    return config;
};
