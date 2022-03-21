import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { IssuesService } from './issues.service';

@Injectable({
  providedIn: 'root'
})
export class ProjectGuard implements CanActivate {

  constructor(private issuesService: IssuesService, private router: Router) {
  }

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    let project = this.issuesService.selectedProjectSubject.getValue();

    if (project == "" || !project) {
      this.router.navigateByUrl("/projects");
      return false;
    }
    else {
      return true;
    }
  }
  
}
