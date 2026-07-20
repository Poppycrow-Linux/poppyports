mkdir -pv ./overlay/{etc,var} ./overlay/usr/{bin,lib,sbin}

for i in bin lib sbin; do
  ln -sv usr/$i ./overlay/$i
done

case $(uname -m) in
  x86_64) mkdir -pv ./overlay/lib64 ;;
esac

mkdir -pv ./overlay/usr/lib32
ln -sv usr/lib32 ./overlay/lib32
