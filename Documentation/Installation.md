# Installation

## 1. Install Anaconda
Make sure that you have `conda` installed on your machine. To do so, follow the steps provided here: [Conda Installation](https://docs.anaconda.com/free/anaconda/install/index.html). We will use Anaconda to manage our dependencies.

## 2. Install Git
Additionally, you need to install `git` to clone the code on your machine. Follow the steps provided here: [Git Installation](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

## 3. Get the Code

To get the code, we will work with the terminal. Use the provided commands as shown. After each command, press `Enter`.

1. Open a terminal and type `cd your-directory-of-choice`. Press `Enter`. This allows you to navigate to the directory where you want to place the code. Remember where you put the code so you can run it later.
2. Clone the code into your directory by running:

    ```bash
    git clone git@github.com:HannahKniesel/Hefekulturen.git
    ```

   If this is successful, the directory will now contain all the important code.

3. Install dependencies and create a new conda environment. To do this, go into the code directory:

    ```bash
    cd Hefekulturen
    ```

    Then run:

    ```bash
    conda env create -f environment.yml
    ```
