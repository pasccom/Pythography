.. Copyright 2020 Pascal COMBES <pascom@orange.fr>

   Pythography is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   Pythography is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with Pythography. If not, see <http://www.gnu.org/licenses/>

IEEE Xplore
===========

The following classes provide a pythonic interface to IEEE Xplore API. They can be used to retrieve easily bibliography data from IEEE Xplore REST API or to search in IEEE Xplore.

.. autoclass:: ieeexplore.Database
.. automethod:: ieeexplore.Database.query
.. automethod:: ieeexplore.Database.send

.. autoclass:: ieeexplore.Query
.. automethod:: ieeexplore.Query.filterBy
.. automethod:: ieeexplore.Query.sortBy
.. automethod:: ieeexplore.Query.clear
.. automethod:: ieeexplore.Query.reset
.. automethod:: ieeexplore.Query.send
.. automethod:: ieeexplore.Query.limit

.. autoclass:: ieeexplore.ResultSet
.. automethod:: ieeexplore.ResultSet.fetchMore
.. automethod:: ieeexplore.ResultSet.complete

.. autoclass:: ieeexplore.Result
.. autoclass:: ieeexplore.QueryString
.. autoclass:: ieeexplore.Author
