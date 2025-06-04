import type {NextFunction, Request, Response} from 'express'
import raw from 'express'
import createRouter from "express-file-routing"
import ws from "express-ws"
import {Logger} from './utils/logger'

// Configure Logger
const log = new Logger()
log.setJsonLogging(process.env.JSON_LOGGING && process.env.JSON_LOGGING == 'true' ? true : false)
log.setLogLevel(process.env.LOG_LEVEL ? process.env.LOG_LEVEL : "INFO")

// Create webserver
const express = require("express")
const app = express()
const expressWs = require("express-ws")(app)

app.use(raw())

app.use((req:Request, res:Response, next:NextFunction) => {

  //Log the request                                                
  res.on('finish', ()=>{                                   
      //Log the response                                   
      Logger.logResponse(req.url, req.method, res.statusCode)                                                                  
  })

  next()
})

await createRouter(app, {
  additionalMethods: [ "ws" ]
})

Logger.info("Server ist listening on http://localhost:3000")
app.listen(3000)

