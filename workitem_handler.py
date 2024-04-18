from robocorp import workitems


class WorkItemHandler:
    """
    A handler class for managing work items in Robocorp processes.

    This class provides methods to retrieve the current work item's payload
    and update the payload of a work item.
    """
    def __init__(self):
        """
        Initializes the WorkItemHandler instance.
        """
        self.wi = workitems

    def get_current_payload(self):
        """
        Retrieves the payload of the current work item.

        Returns:
            dict: The payload of the current work item.
        """
        item = self.wi.inputs.current
        return item.payload

    def update_payload(self, new_payload):
        """
        Updates the payload of the current work item with a new payload.

        Args:
            new_payload (dict): The new payload to update the current work item with.
        """
        self.wi.outputs.create(payload=new_payload)