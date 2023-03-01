for x in $* ; do
  scp -i ~/.ssh/codebang_id_rsa $x root@codebang.com:/home/jondy/pyarmor-docs/$x
done

