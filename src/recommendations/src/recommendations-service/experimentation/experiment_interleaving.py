# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import random
import time
import logging

from botocore.exceptions import ClientError
from experimentation.experiment import Experiment

log = logging.getLogger(__name__)

class InterleavingExperiment(Experiment):
    """ Implements interleaving technique described in research paper by 
    Chapelle et al http://olivier.chapelle.cc/pub/interleaving.pdf
    """
    METHOD_BALANCED = 'balanced'
    METHOD_TEAM_DRAFT = 'team-draft'

    def __init__(self, table, **data):
        super(InterleavingExperiment, self).__init__(table, **data)
        self.method = data.get('method', InterleavingExperiment.METHOD_BALANCED)

    def get_items(self, user_id, current_item_id = None, item_list = None, num_results = 10, tracker = None):
        if not user_id:
            raise Exception('user_id is required')
        if len(self.variations) < 2:
            raise Exception(f'Experiment {self.id} does not have 2 or more variations')

        # Initialize array structure to hold item recommendations for each variation
        variations_data = [[] for x in range(len(self.variations))]

        resolve_params = {
            'user_id': user_id,
            'product_id': current_item_id,
            'product_list': item_list,
            'num_results': num_results * 3  # account for overlaps
        }

        # Get recomended items for each variation
        for i in range(len(self.variations)):
            variation = self.variations[i]
            items = variation.resolver.get_items(**resolve_params)
            variations_data[i] = items

        # Interleave items to produce result
        interleaved = []
        if self.method == InterleavingExperiment.METHOD_TEAM_DRAFT:
            interleaved = self._interleave_team_draft(user_id, variations_data, num_results)
        else:
            interleaved = self._interleave_balanced(user_id, variations_data, num_results)

        # Increment exposure for each variation (can be optimized)
        for i in range(len(self.variations)):
            self._increment_exposure_count(i)

        if tracker is not None:
            # Track exposure details
            track_interleaved = []
            for item in interleaved:
                track_interleaved.append({
                    'item_id': item['itemId'],
                    'variation_index': item['experiment']['variationIndex']
                })

            event = {
                'event_type': 'Experiment Exposure',
                'event_timestamp': int(round(time.time() * 1000)),
                'attributes': {
                    'user_id': user_id,
                    'experiment': {
                        'id': self.id,
                        'feature': self.feature,
                        'name': self.name,
                        'type': self.type,
                        'method': self.method
                    },
                    'interleaved': track_interleaved
                }
            }

            tracker.log_exposure(event)

        return interleaved

    """
    Implements the balanced interleaving method described in the Interleaving 
    research paper by Chapelle et al http://olivier.chapelle.cc/pub/interleaving.pdf

    The paper describes interleaving results from two rankings, A and B, but 
    this implementation supports interleaving from more than two rankings.

    Pseudo logic:

    Input: two or more lists of rankings (2 rankings A & B is typical)
    Init: randomize order of rankings to set selection order

    while (not at the end of any ranking) do 
        determine the first ranking that has contributed the fewest items to results
        if (next item from ranking is not in results) then
            add next item from ranking to results
        end if
        increment next item offset for ranking
    end while

    Output: list of interleaved results from all rankings
    """
    def _interleave_balanced(self, user_id, list_of_item_lists, count):
        """ Returns interleaved list of items following the balanced method """
        # Randomize selection order of lists
        selection_order = list(range(len(list_of_item_lists)))
        random.shuffle(selection_order)

        # Holds next selection offset into each variation list
        offsets = [0] * len(list_of_item_lists)

        result = []
        while len(result) < count:
            # Find lowest offset to determine which variation list to pull next result
            next_idx = 0
            for i in range(len(offsets)):
                if (offsets[i] < offsets[next_idx] and 
                        offsets[i] < len(list_of_item_lists[selection_order[i]])):
                    next_idx = i

            # As soon as we reach end of a variation list, we're done
            if offsets[next_idx] >= len(list_of_item_lists[selection_order[next_idx]]):
                break

            # Add value to result if not already there
            item = list_of_item_lists[selection_order[next_idx]][offsets[next_idx]]
            if not any(i['itemId'] == item['itemId'] for i in result):
                variation_idx = selection_order[next_idx]
                correlation_id = self._create_correlation_id(user_id, variation_idx, len(result) + 1)

                item_experiment = {
                    'id': self.id,
                    'feature': self.feature,
                    'name': self.name,
                    'type': self.type,
                    'method': self.method,
                    'variationIndex': variation_idx,
                    'resultRank': len(result) + 1,
                    'correlationId': correlation_id
                }

                item.update({ 
                    'experiment': item_experiment
                })

                result.append(item)
            
            offsets[next_idx] = offsets[next_idx] + 1 
        
        return result

    """
    Implements the team-draft interleaving method described in the Interleaving 
    research paper by Chapelle et al http://olivier.chapelle.cc/pub/interleaving.pdf

    The paper describes interleaving results from two rankings, A and B, but 
    this implementation supports interleaving from more than two rankings.

    Pseudo logic:

    Input: two or more lists of rankings (2 rankings A & B is typical)
    Init: Roster (list) for each team/ranking as players/items are selected

    while (not at the end of any team's ranking) do 
        determine list of teams with smallest size
        if (there are multiple teams with smallest size) then
            randomly select a team from this list to select next
        end if
        if (next top item/player for team's ranking is not in results) then
            add top item/player from team's ranking to results
            add top item/player from team's ranking to team's roster
        end if
    end while

    Output: list of interleaved results from all rankings
    """
    def _interleave_team_draft(self, user_id, list_of_item_lists, count):
        """ Returns interleaved list of items following the team draft method """
        # List of team rosters
        teams = [[] for x in range(len(list_of_item_lists))]

        # Offsets into list of item lists
        offsets = [0] * len(list_of_item_lists)

        result = []
        while len(result) < count:
            # Team offsets keyed by team size
            size_teams = {}
            for i in range(len(teams)):
                team_size = len(teams[i])
                teams_at_size = size_teams.get(team_size, [])
                teams_at_size.append(i)
                size_teams[team_size] = teams_at_size

            # List of team offsets with smallest size
            ordered_keys = sorted(size_teams.keys())
            smallest_teams = size_teams.get(ordered_keys[0])

            # Choose an offset at random from smallest team offsets
            team_index = random.choice(smallest_teams)

            next_offset = offsets[team_index]
            items = list_of_item_lists[team_index]

            while next_offset < len(items):
                offsets[team_index] = next_offset + 1

                item = items[next_offset]
                if not any(i['itemId'] == item['itemId'] for i in result):
                    correlation_id = self._create_correlation_id(user_id, team_index, len(result) + 1)

                    item_experiment = {
                        'id': self.id,
                        'feature': self.feature,
                        'name': self.name,
                        'type': self.type,
                        'method': self.method,
                        'variationIndex': team_index,
                        'resultRank': len(result) + 1,
                        'correlationId': correlation_id
                    }

                    item.update({ 
                        'experiment': item_experiment
                    })

                    # Add item to result and team roster
                    result.append(item)
                    teams[team_index].append(item)
                    break

                next_offset += 1

            # If at end of any items list, done
            if next_offset >= len(items):
                break

        return result