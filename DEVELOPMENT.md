## Install package manager

### pnpm

Using corepack:

```shell
corepack prepare pnpm@latest --activate
```

or using `npm`:

```shell
npm install -g pnpm@latest
```

Verify the latest version.

```shell
pnpm --version
```

### Install dependencies

In order to develop `collective.z3cform.datagridfield` JS/SCSS files you need to execute on the root of the package::

```shell
pnpm install
```

You can also updated dependencies with

```shell
pnpm update
```

or you can inspect latest versions of dependencies with

```shell
pnpm update --interactive --latest
```

After executing this you can run the following command to watch for any scss changes
in the path `collective.z3cform.datagridfield/resources`::

```shell
pnpm watch
```

This will make sure that the many .scss files are compiled to .css on the fly
and then copied over to the theme.

If you simply want to compile all resources before a release run::

```shell
pnpm build
```
