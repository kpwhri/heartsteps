import { Injectable } from "@angular/core";
import { Resolve, ActivatedRouteSnapshot, RouterStateSnapshot } from "@angular/router";
import { AppService } from "./app.service";


@Injectable()
export class AppReadyResolver implements Resolve<boolean> {

    constructor(
        private appService: AppService
    ) {}

    resolve(): boolean | Promise<boolean> {
        console.log('AppReadyResolver', 'starting....')
        return this.appService.ready.first().toPromise()
        .then(() => {
            console.log('AppReadyResolver', 'finished');
            return true;
        });
    }

}