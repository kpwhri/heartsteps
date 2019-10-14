import { Injectable } from "@angular/core";
import { CanActivate, Router } from "@angular/router";
import { AuthorizationService } from "@infrastructure/authorization.service";

@Injectable()
export class BaselineWeekGaurd implements CanActivate {

    constructor(
        private authorizationService: AuthorizationService,
        private router: Router
    ){}

    canActivate():Promise<boolean> {
        return this.authorizationService.isAuthorized()
        .then(() => {
            return true;
        })
        .catch(() => {
            this.router.navigate(['welcome']);
            return false;
        });
    }

}
