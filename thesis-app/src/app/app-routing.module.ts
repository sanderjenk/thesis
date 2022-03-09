import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { IntroComponent } from './intro/intro.component';
import { IssuesComponent } from './issues/issues.component';
import { ProjectGuard } from './project.guard';
import { ProjectsComponent } from './projects/projects.component';
import { SelectedIssuesComponent } from './selected-issues/selected-issues.component';

const routes: Routes = [
  { 
    path: '', 
    component: IntroComponent 
  },
  { 
    path: 'issues', 
    component: IssuesComponent, 
    // canActivate: [ProjectGuard] 
  },
  { 
    path: 'selected', 
    component: SelectedIssuesComponent, 
    // canActivate: [ProjectGuard]
},
  { 
    path: 'projects', 
    component: ProjectsComponent 
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
