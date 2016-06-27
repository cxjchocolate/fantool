#!/usr/bin/sh
#
#@author caixiong @created 2015/8/20
#

#
# set the environments for running
#
.  /etc/profile

HAIYAN_HOME=/data/svn/Haiyan
SOA_HOME=/data/svn/SOA
SCM_HOME=/data/svn/SOA
ORDERUI_HOME=/data2/svn/OrderUI
module=$1
version=$2
user=deploy
password=deploy


#set "store-passwords = no" 
#in /$USER_HOME/.subversion/servers

if [ -z "$JAVA_HOME" ]
then
echo "JAVA_HOME not defined"
exit
fi

if [ -z "$ANT_HOME" ]
then
echo "ANT_HOME not defined"
exit
fi

if [ -z "$user" ]
then
echo "svn user is null"
exit
fi

if [ -z "$password" ]
then
echo "svn password is null"
exit
fi

if [ -z "$module" ];then
  echo "INFO: no module defined"
  basepath=$(cd `dirname $0`; pwd)
  
  echo "INFO: Use name of xml as parameters"
  echo "INFO: command 'package activity'"
  cd $basepath/conf
  ls *.xml
  exit
fi

if [ "$module" = "haiyan" ] && [ -z "$version" ];then
	echo "INFO: haiyan must be with version"
	exit
fi

cd `dirname $0`
ant -buildfile conf/$module.xml -Dsoa=$SOA_HOME -Dhaiyan=$HAIYAN_HOME -Dscm=$SCM_HOME -Dorderui=$ORDERUI_HOME -Dsvn.user=$user -Dversion=$version -Dsvn.password=$password
