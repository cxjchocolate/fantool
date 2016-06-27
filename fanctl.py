# -*- coding: gbk -*-
'''
Created on 2015年11月1日

@author: 大雄
'''
import argparse
import logging
import sys

import env
from openapi import OpenAPI
import utils
from db import AppHistory


if __name__ == '__main__':
    
    machine, ipaddr = utils.getHostInfo()
    e = utils.Namespace()
    setattr(e, "machine", machine)
    setattr(e, "ipaddr", ipaddr)
    setattr(e, "username", utils.getCurrentUser())
    setattr(e, "program", "fanctl")
    
    def deployApp(args):
        OpenAPI("openapi", None, "deployApp",
                args=(args.brand.upper(), args.module.upper(), args.master_rev, args.config_rev),
                env=e).call()
                
    def rollbackApp(args):
        OpenAPI("openapi", None, "rollbackApp",
                args=(args.brand.upper(), args.module.upper()),env=e).call()

    def stopServer(args):
        # stopServer(args.brand, args.res)
        OpenAPI("openapi", None, "stopServer", args=(args.brand, args.res), env=e).call()
 
 
    def startServer(args):
        # startServer(args.brand, args.res)
        OpenAPI("openapi", None, "startServer", args=(args.brand, args.res), env=e).call()
       

    def restartServer(args):
        # restartServer(args.brand, args.res)
        OpenAPI("openapi", None, "restartServer", args=(args.brand, args.res), env=e).call()
 
        
    parser = argparse.ArgumentParser(prog='fanctl')
    subparser = parser.add_subparsers(title="Command")
    p_deploy = subparser.add_parser('deploy')
    p_rollback = subparser.add_parser('rollback')
    p_stop = subparser.add_parser('stop')
    p_start = subparser.add_parser('start')
    p_restart = subparser.add_parser('restart')
    
    # subcommand deploy
    sub_deploy = p_deploy.add_subparsers(title="Command")
    p_deployapp = sub_deploy.add_parser("app") 
    p_deployapp.set_defaults(func=deployApp)
    p_deployapp.add_argument('-b', "--brand",
              action="store",
              dest="brand"  ,
              required=True,
              default=None, help='Specify brand for deployment'  
                ) 
    
    p_deployapp.add_argument("-m", "--module",
                action="store",
                dest="module",
                required=True,
                default=None, help='Specify module for deployment' 
                )  
     
    p_deployapp.add_argument("-v", "--master_rev",
                action="store",
                dest="master_rev",
                default="HEAD" , help="Specify the revision of module"  
                ) 

    p_deployapp.add_argument("-w", "--config_rev",
                action="store",
                dest="config_rev",
                default="HEAD" , help="Specify the revision of config"  
                ) 
    # subcommand rollback
    sub_rollback = p_rollback.add_subparsers(title="Command")
    p_rollbackapp = sub_rollback.add_parser("app") 
    p_rollbackapp.set_defaults(func=rollbackApp)
    p_rollbackapp.add_argument('-b', "--brand",
              action="store",
              dest="brand"  ,
              required=True,
              default=None, help='Specify brand for rollback'  
                ) 
    
    p_rollbackapp.add_argument("-m", "--module",
                action="store",
                dest="module",
                required=True,
                default=None, help='Specify module for rollback' 
                )
    
    
    # subcommand stop
    sub_stop = p_stop.add_subparsers(title="Object")
    p_stopserver = sub_stop.add_parser("server")
    p_stopserver.set_defaults(func=stopServer)    
    p_stopserver.add_argument("--brand", '-b',
              action="store",
              dest="brand"  ,
              required=True,
              default=None, help='Specify which server to stop'
              )
    p_stopserver.add_argument('-s', "--res",
              action="store",
              dest="res"  ,
              required=True,
              default=None, help='Specify which server to stop'
              )

    # subcommand restart
    sub_restart = p_restart.add_subparsers(title="Object")
    p_restartserver = sub_restart.add_parser("server")
    p_restartserver.set_defaults(func=restartServer)    
    p_restartserver.add_argument("--brand", '-b',
              action="store",
              dest="brand"  ,
              required=True,
              default=None, help='Specify which server to restart'
              )
    p_restartserver.add_argument('-s', "--res",
              action="store",
              dest="res"  ,
              required=True,
              default=None, help='Specify which server to stop'
              )


    # subcommand start
    sub_start = p_start.add_subparsers(title="Object")
    p_startserver = sub_start.add_parser("server")
    p_startserver.set_defaults(func=startServer)    
    p_startserver.add_argument("--host",
              action="store",
              dest="host"  ,
              required=True,
              default=None, help='Specify which server to start'
              )   
    p_startserver.add_argument('-s', "--server",
              action="store",
              dest="server"  ,
              required=True,
              default=None, help='Specify which server to start'
              )

    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s [%(levelname)s] %(filename)s[line:%(lineno)d] %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S')
    env.configure("conf.ini")
    '''
    print(     
   
  Welcome to  
            _____       ___   __   _   _____   _____   _      
           |  ___|     /   | |  \ | | /  ___| |_   _| | |     
           | |__      / /| | |   \| | | |       | |   | |     
           |  __|    / / | | | |\   | | |       | |   | |     
           | |      / /  | | | | \  | | |___    | |   | |___  
           |_|     /_/   |_| |_|  \_| \_____|   |_|   |_____|  version 2.0

    )
    '''
    '''
#   args = parser.parse_args("start server -h".split())
    print("About fanctl,Please visit")
    print("http://it.zaofans.com:8070/trac/zaofans/wiki/Env/OP")
    print("for detail")
    print("")
    '''
    
    args = parser.parse_args()
    logging.debug(args)
    if len(sys.argv) > 1:
        args.func(args)
    else:
        print("fanctl -h for help")   
