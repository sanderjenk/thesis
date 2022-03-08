import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { IssuesService } from '../issues/issues.service';
import { Project } from './project';

@Component({
  selector: 'app-projects',
  templateUrl: './projects.component.html',
  styleUrls: ['./projects.component.css']
})
export class ProjectsComponent implements OnInit {

  displayedColumns: string[] = ['project_key', 'description', 'programing_language', 'purpose', 'buttons'];
  dataSource: Project[] = [];

  constructor(
    private issuesService: IssuesService,
    private route: ActivatedRoute,
    private router: Router) { }

  ngOnInit(): void {
    this.issuesService.getProjects().subscribe((x: any[]) => this.dataSource = x)
  }

  selectProject(key: string){
    this.issuesService.selectProject(key);
    this.router.navigate(["/issues"], {relativeTo: this.route})
  }

}
