# Metravision

Detecting and counting light vehicles (motorbikes and alikes) on highways,
using learning algorithmes.

Currently, the *project* is **based** on it's little-brother, Traqu'moto, made
in 2017. It uses Torch and OpenCV and is available under the BSD-3-Clause
license.

## Installing

The project depends on anaconda packages. To retrieve them, you should install miniconda or anaconda, then use

```sh
conda install -c conda-forge opencv pyyaml ipython
```

to install them. If you are on Windows, you'll want to use the Anaconda Prompt.
If you want to develop the project, you may want to install the python packages `pylint` and `rope`. You can do so with the command:

```sh
conda install pylint rope
```

## Using git

Below is the subset of the most basic git commands you need to know to work
on a git project.

To get a more robust presentation of git basics, you might want to read the
page [Learn git in Y minutes](https://learnxinyminutes.com/docs/git/).
The below command presentations are copy-pasted from that page. This page
will likely be harder to understand than the above linked page.

### Récapitulatif des commandes

![Git data transport commands](https://i.stack.imgur.com/MgaV9.png)

Source: [q/2745076](https://stackoverflow.com/q/2745076)

### Détail des commandes

#### config

To configure settings. Whether it be for the repository, the system itself,
or global configurations ( global config file is `~/.gitconfig` ).

```bash
# Print & Set Some Basic Config Variables (Global)
$ git config --global user.email "MyEmail@Zoho.com"
$ git config --global user.name "My Name"
```

[Learn More About git config.](http://git-scm.com/docs/git-config)

#### help

To give you quick access to an extremely detailed guide of each command. Or to
just give you a quick reminder of some semantics.

```bash
# Quickly check available commands
$ git help

# Check all available commands
$ git help -a

# Command specific help - user manual
# git help <command_here>
$ git help add
$ git help commit
$ git help init
# or git <command_here> --help
$ git add --help
$ git commit --help
$ git init --help
```

#### clone

Clones, or copies, an existing repository into a new directory. It also adds
remote-tracking branches for each branch in the cloned repo, which allows you
to push to a remote branch.

```bash
# Clone learnxinyminutes-docs
$ git clone https://github.com/adambard/learnxinyminutes-docs.git

# shallow clone - faster cloning that pulls only latest snapshot
$ git clone --depth 1 https://github.com/adambard/learnxinyminutes-docs.git

# clone only a specific branch
$ git clone -b master-cn https://github.com/adambard/learnxinyminutes-docs.git --single-branch
```

#### status

To show differences between the index file (basically your working copy/repo)
and the current HEAD commit.

```bash
# Will display the branch, untracked files, changes and other differences
$ git status

# To learn other "tid bits" about git status
$ git help status
```

#### add

To add files to the staging area/index. If you do not `git add` new files to
the staging area/index, they will not be included in commits!

```bash
# add a file in your current working directory
$ git add HelloWorld.java

# add a file in a nested dir
$ git add /path/to/file/HelloWorld.c

# Regular Expression support!
$ git add ./*.java

# You can also add everything in your working directory to the staging area.
$ git add -A
```

This only adds a file to the staging area/index, it doesn't commit it to the
working directory/repo.

#### commit

Stores the current contents of the index in a new "commit." This commit
contains the changes made and a message created by the user.

```bash
# commit with a message
$ git commit -m "Added multiplyNumbers() function to HelloWorld.c"

# signed commit with a message (user.signingkey must have been set
# with your GPG key e.g. git config --global user.signingkey 5173AAD5)
$ git commit -S -m "signed commit message"

# automatically stage modified or deleted files, except new files, and then commit
$ git commit -a -m "Modified foo.php and removed bar.php"

# change last commit (this deletes previous commit with a fresh commit)
$ git commit --amend -m "Correct message"
```

#### log

Display commits to the repository.

```bash
# Show all commits
$ git log

# Show only commit message & ref
$ git log --oneline

# Show merge commits only
$ git log --merges

# Show all commits represented by an ASCII graph
$ git log --graph
```

#### pull

Pulls from a repository and merges it with another branch.

```bash
# Update your local repo, by merging in new changes
# from the remote "origin" and "master" branch.
# git pull <remote> <branch>
$ git pull origin master

# By default, git pull will update your current branch
# by merging in new changes from its remote-tracking branch
$ git pull

# Merge in changes from remote branch and rebase
# branch commits onto your local repo, like: "git fetch <remote> <branch>, git
# rebase <remote>/<branch>"
$ git pull origin master --rebase
```

#### push

Push and merge changes from a branch to a remote & branch.

```bash
# Push and merge changes from a local repo to a
# remote named "origin" and "master" branch.
# git push <remote> <branch>
$ git push origin master

# By default, git push will push and merge changes from
# the current branch to its remote-tracking branch
$ git push

# To link up current local branch with a remote branch, add -u flag:
$ git push -u origin master
# Now, anytime you want to push from that same local branch, use shortcut:
$ git push
```
