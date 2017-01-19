open (IN, $ARGV[0]);

while (<IN>)
{
  if (/(\d+)/) { print "$1,"; }
}
