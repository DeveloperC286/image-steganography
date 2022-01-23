VERSION 0.6


clean-git-history-checking:
    FROM rust
    RUN cargo install clean_git_history
	COPY ".git" "."
	ARG from="origin/HEAD"
	RUN /usr/local/cargo/bin/clean_git_history --from-reference "${from}"


conventional-commits-linting:
    FROM rust
    RUN cargo install conventional_commits_linter
    COPY ".git" "."
    ARG from="origin/HEAD"
    RUN /usr/local/cargo/bin/conventional_commits_linter --from-reference "${from}" --allow-angular-type-only


formatting-base:
    FROM python:3-slim
    RUN pip3 install "autopep8"
    COPY "*.py" "."


check-formatting:
    FROM +formatting-base
    RUN find "." -maxdepth 1 -type f -name "*.py" | xargs -I {} autopep8 --exit-code --diff --aggressive --aggressive "{}"


fix-formatting:
    FROM +formatting-base
    RUN find "." -maxdepth 1 -type f -name "*.py" | xargs -I {} autopep8 --in-place --aggressive --aggressive "{}"
    SAVE ARTIFACT "*.py" AS LOCAL "./"


python2-base:
    FROM python:2
    COPY "requirements.txt" "."
    RUN pip2 install -r "requirements.txt"
    COPY "*.py" "."


compiling:
    FROM +python2-base
    RUN find "." -maxdepth 1 -type f -name "*.py" | xargs -I {} python2 -m py_compile "{}"


end-to-end-tests:
    BUILD +non-encrypted-end-to-end-test
    BUILD +encrypted-end-to-end-test


end-to-end-test-base:
    FROM +python2-base
    RUN curl "https://png.pngtree.com/element_our/sm/20180327/sm_5aba147bcacf2.png" > "input.image.png"
    RUN echo "12345" > "input.data"


non-encrypted-end-to-end-test:
    FROM +end-to-end-test-base
    RUN python2 "image-steganography.py" --encode --input "input.image.png" --data "input.data" --output "output.image.png"
    RUN python2 "image-steganography.py" --decode --input "output.image.png" --output "output.data"
    RUN cmp --silent "input.data" "output.data"


encrypted-end-to-end-test:
    FROM +end-to-end-test-base
    RUN python2 "image-steganography.py" --encode --input "input.image.png" --data "input.data" --output "output.image.png" --key "1234567890123456"
    RUN python2 "image-steganography.py" --decode --input "output.image.png" --output "output.data" --key "1234567890123456"
    RUN cmp --silent "input.data" "output.data"
