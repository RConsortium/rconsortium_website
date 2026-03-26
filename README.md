## What is the R Consortium?

The R Consortium, Inc. is a group organized under an open source governance and foundation model to support the worldwide community of users, maintainers and developers of R software. Its [members](https://www.r-consortium.org/members) include leading institutions and companies dedicated to the use, development and growth of R.

The R language is an open source environment for statistical computing and graphics. The R community has enjoyed significant growth, with more than 2 million users worldwide. A broad range of organizations have adopted the R language as a data science platform, including biotech, finance, research and high technology industries. The R language is often integrated into third-party analysis, visualization and reporting applications, and runs on a wide variety of computing platforms.

The R Consortium’s mission is to promote the R language and to develop the technical and social infrastructure required to support the R ecosystem and the R Community. Its activities and programs include:

Promoting the growth and development of R as a leading platform for data science and statistical computing. [Members of the R Consortium](https://www.r-consortium.org/members) are recognized as supporters of the R Project and the R community, and the R Consortium represents its members to the R community and to the media. Supporting and collaborating with the [R Foundation](https://www.r-project.org/foundation/), the governing body of the R Project.

The R Foundation maintains a permanent seat on the board of the R Consortium, as an open communication channel for R Consortium members.

Funding projects to enhance R and support its users.

Projects are proposed by the R community at large, and selected for funding by the Infrastructure Steering Committee. R Consortium members nominate the selection committee and provide funds for project grants with their membership dues. (Here is a list of [projects funded by the R Consortium](https://www.r-consortium.org/all-projects/funded-projects) to date.)

Fostering the continued growth of R community and the data science ecosystem.

The R Consortium sponsors R-related conferences (including useR!), meetings (including SatRDays and RLadies), and local user groups worldwide.

Enabling the use of R in commercial environments, and fostering collaboration between companies investing in R.  
R Consortium committees are developing programs for R language certification and training, consulting, and employment.

The mission of the R Consortium is formally defined in the [R Consortium bylaws](https://www.r-consortium.org/rc-docs/Bylaws-GU-Draft-7-9-2024.docx.pdf) (PDF) and the [Infrastructure Steering Committee charter](https://www.r-consortium.org/rc-docs/ISC-Charter-08-13-24.pdf) (PDF).

## Main Links

Main Site (this site): [https://www.r-consortium.org/](https://www.r-consortium.org/)  
Join: [https://www.r-consortium.org/about/join](https://www.r-consortium.org/about/join)  

Blog: [https://www.r-consortium.org/news/blog](https://www.r-consortium.org/news/blog)  
LinkedIn: [https://www.linkedin.com/company/r-consortium/](https://www.linkedin.com/company/r-consortium/)  
Bluesky: [https://bsky.app/profile/rconsortium.bsky.social](https://bsky.app/profile/rconsortium.bsky.social)  
Fosstodon: [https://fosstodon.org/@RConsortium](https://fosstodon.org/@RConsortium)  

---

# Contributing to the R Consortium Website

This website is built members of the R Consortium, and a wide range of contributors and helpers include R-Ladies Gaborone and other volunteers. There are many blog posts from R Consortium ISC technology projects, helping to build R infrastructure. And many from R User Groups around the world learning R, promoting R, making connections to local industry, and much more. There are also many R experts and enthusiasts giving webinars and sharing their expertise. And multiple annual events, including R+AI, R/Medicine, Risk and userR!, that are directly hosted or sponsored by the R Consortium. 

Thank you to all our contrubitors and volunteers! 

If you want to help contribute to the site, please use the following workflow.

### Workflow for making contributions

#### 1. Fork this website

#### 2. Make a branch

Pull down the fork locally, make a branch and edit your branch locally.

To preview the website locally and your new edits:

```bash
quarto preview
```

Ensure you are in the root directory of the Quarto project where the _quarto.yml file is located.

**Note:** This website uses Quarto's freeze feature to optimize rendering performance. The freeze feature caches computational results and only re-renders posts when their content has changed. This prevents unnecessary re-rendering of all 250+ posts when only one post is modified, making it much faster to contribute to the website. However, the first time you render the site locally, you will be rendering a large group of files. This is normal.

The freeze cache is stored in the `_freeze/` directory and should be committed to version control to ensure consistency across different environments.

#### 3. Commit your changes

Make your changes locally, save them and commit them. Please make your commit message descriptive of the work you did.

#### 4. Do a Pull Request

Push up to your own forked repo. Then do a pull request to the R Consortium website repo. We will review your Pull Request!

## If your system has not run a Quarto site before...

## Install Quarto

If you need to install Quarto locally, please see: [https://quarto.org/docs/get-started/](https://quarto.org/docs/get-started/)

## Make sure you have R and two important R libraries

Install R using `sudo apt-get install r-base` and `sudo apt-get install r-base-dev`

Install R packages on Linux; type R in console and then `install.packages('rmarkdown')`

GGPLOT2 installation: `install.packages("ggplot2")`

dygraphs installation : `install.packages("dygraphs")`

## Some Info on .gitignore

The .gitignore of this project is setup to ignore `_site/`, `.quarto/` and `docs`

![gitignore](/images/gitignore.png)

- `_site/` is also known as `docs/` in other quarto projects

- `_site` was specified as netlify publish directory on the website 

- `docs/` 

### RStudio Workflow

Make sure you have RStudio installed. The RStudio IDE is still called "RStudio." The company has changed its name to Posit. Posit is an R Consortium Platinum member.

Fork this [Github public repo](https://github.com/RConsortium/rconsortium_website) to your own GitHub account. Then pull it down to your local machine.

Open the rconsortium_website project in RStudio (File → Open Project). Ensure that you’ve switched to a new branch. `git checkout -b name_new_branch`

Install renv with `install.packages(“renv”)` in console

Run `renv::restore()` in console

Open a file for testing. Make edits to the file and run `render` in RStudio to view the updates.

## Push Up and Create Pull Request

Once finished with editing, run `git add`, `git commit`, and `git push` to your fork on GitHub.

Make a Pull Request!

A reviewer will test your Pull Request and get back to you within just a couple of days.

### VSCode Workflow

If you’re using VS Code, start R.

Install R `languageserver` when prompted.

Install packages for R extension on VS Code.

Run `install.packages("renv")` and `renv::restore()` in the terminal.

Make edits to a file and run `quarto render` and `quarto preview` to see the changes.