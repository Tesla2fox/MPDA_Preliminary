# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 20:59:23 2018

@author: robot
"""

import plotly.plotly as py
import plotly.figure_factory as ff
import plotly


#plotly.figure_factory

df = [dict(Task="Job A", Start='1', Finish='3'),
      dict(Task="Job B", Start='0', Finish='4'),
      dict(Task="Job C", Start='3', Finish='5')]




import plotly.plotly as py
import plotly.figure_factory as ff

df = [dict(Task='Agent-0', Start='1', Finish='4', Resource='Complete'),
      dict(Task="Job-1", Start='2', Finish='3', Resource='Incomplete'),
      dict(Task="Job-2", Start='3', Finish='2', Resource='Not Started'),
      dict(Task="Job-2", Start='4', Finish='9', Resource='Complete'),
#      dict(Task="Job-3", Start='5', Finish='2017-03-20', Resource='Not Started'),
#      dict(Task="Job-3", Start='1', Finish='2017-04-20', Resource='Not Started'),
#      dict(Task="Job-3", Start='2017-05-18', Finish='2017-06-18', Resource='Not Started'),
#      dict(Task="Job-4", Start='2017-01-14', Finish='2017-03-14', Resource='Complete')
      ]

colors = {'Not Started': 'rgb(220, 0, 0)',
          'Incomplete': (1, 0.9, 0.16),
          'Complete': 'rgb(0, 255, 100)'}

fig = ff.create_gantt(df, colors=colors, index_col='Resource', show_colorbar=True, group_tasks=True)

fig['layout']['xaxis']['type'] = 'linear'

plotly.offline.plot(fig, filename='gantt-group-tasks-together')

#fig = ff.create_gantt(df)
#
##print(fig)
#fig['layout']['xaxis']['type'] = 'linear'
#
#plotly.offline.plot(fig, filename='gantt-simple-gantt-chart')
