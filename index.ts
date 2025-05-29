import type {Request, Response} from 'express'
import raw from 'express'
import createRouter from "express-file-routing"
import ws from "express-ws"

const { app } = ws(require('express')())

app.use(raw())

await createRouter(app, {
  additionalMethods: [ "ws" ]
})

app.use((req:Request, res:Response) => {
  console.log(req.url)
  console.log(req.method)
  console.log(req.headers)
})

app.listen(3000)


