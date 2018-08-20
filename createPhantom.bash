#!/usr/bin/env bash
rm -rf tmp
mkdir tmp
xmipp_transform_geometry -i reference.jpg --shift  5  5 -o tmp/01.jpg # 0
xmipp_transform_geometry -i reference.jpg --shift  5 -5 -o tmp/02.jpg # 1
xmipp_transform_geometry -i reference.jpg --shift -5  5 -o tmp/03.jpg # 7
xmipp_transform_geometry -i reference.jpg --shift -5 -5 -o tmp/04.jpg # 8

xmipp_transform_geometry -i reference.jpg --shift  0  7 -o tmp/05.jpg # 2
xmipp_transform_geometry -i reference.jpg --shift  0 -7 -o tmp/06.jpg # 3
xmipp_transform_geometry -i reference.jpg --shift  7  0 -o tmp/07.jpg # 5
xmipp_transform_geometry -i reference.jpg --shift -7  0 -o tmp/08.jpg # 6

#xmipp_transform_geometry -i reference.jpg --shift  1 -4 -o tmp/09.jpg
#xmipp_transform_geometry -i reference.jpg --shift -1  4 -o tmp/10.jpg
#xmipp_transform_geometry -i reference.jpg --shift  4  1 -o tmp/11.jpg
#xmipp_transform_geometry -i reference.jpg --shift -4 -1 -o tmp/12.jpg

#xmipp_transform_geometry -i reference.jpg --shift -1 -4 -o tmp/13.jpg
#xmipp_transform_geometry -i reference.jpg --shift  4 -1 -o tmp/14.jpg
#xmipp_transform_geometry -i reference.jpg --shift  4  1 -o tmp/15.jpg
#xmipp_transform_geometry -i reference.jpg --shift -4  1 -o tmp/16.jpg

xmipp_image_convert -i tmp/01.jpg -o tmp/phantom.stk --append
xmipp_image_convert -i tmp/02.jpg -o tmp/phantom.stk --append
xmipp_image_convert -i tmp/05.jpg -o tmp/phantom.stk --append
xmipp_image_convert -i tmp/06.jpg -o tmp/phantom.stk --append
#xmipp_image_convert -i tmp/09.jpg -o tmp/phantom.stk --append
#xmipp_image_convert -i tmp/10.jpg -o tmp/phantom.stk --append
#xmipp_image_convert -i tmp/13.jpg -o tmp/phantom.stk --append
#xmipp_image_convert -i tmp/14.jpg -o tmp/phantom.stk --append
xmipp_image_convert -i reference.jpg -o tmp/phantom.stk --append
#xmipp_image_convert -i tmp/15.jpg -o tmp/phantom.stk --append
#xmipp_image_convert -i tmp/16.jpg -o tmp/phantom.stk --append
#xmipp_image_convert -i tmp/11.jpg -o tmp/phantom.stk --append
#xmipp_image_convert -i tmp/12.jpg -o tmp/phantom.stk --append
xmipp_image_convert -i tmp/07.jpg -o tmp/phantom.stk --append
xmipp_image_convert -i tmp/08.jpg -o tmp/phantom.stk --append
xmipp_image_convert -i tmp/03.jpg -o tmp/phantom.stk --append
xmipp_image_convert -i tmp/04.jpg -o tmp/phantom.stk --append

# 0 -> 1 (0,10)
# 0 -> 2 (5,2)
# 0 -> 3 (5,12)
# 0 -> 4 (5,5)
# 0 -> 5 (2,-5)
# 0 -> 6 (12,5)
# 0 -> 7 (-10,0)
# 0 -> 8 (10,10)


mv tmp/phantom.stk .
rm -rf tmp

