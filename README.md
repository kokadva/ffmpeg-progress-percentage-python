### FFmpeg progress percentage

#### Description:
In this project I print out ffmpeg processing percentage. As I'm doing
the conversion the result file will have the same duration as the
target so every time a progress log appears I take how much seconds it
has already processed and divide it to target file's length. In other
cases like speeding up/down, cutting, merging and etc. this won't work
so percentage computation must be changed.

### Author:
* Konstantine Dvalishvili konstantine.dvalishvil@gmail.com