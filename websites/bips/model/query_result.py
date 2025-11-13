
class query_result():
    """
        Class query_result for storing the result of an SQL query.
    """

    def __init__(self, query, params):
        self.query = query  # initial query (possibbly with placeholders)
        self.is_select_query = True  # select/set query or insert/update/delete query
        self.params = params  # initial params for the query
        self.full_query = None  # query built by Postgresql (given query and params)
        self.statusmessage = None
        self.error_code = None  # error code number
        self.error_type = None  # error type (ERROR, ...)
        self.error_message = None  # error message
        self.error_detail = None  # detailed error message
        self.result_instances = None  # list of result instances for select/show queries
        self.result_attributes = None  # list of attributes names for select/show queries
        self.result_affected_rows = None  # number of affected rows (insert/delete/update/... queries)

    def __repr__(self):
        return self.__str__

    def __str__(self):
        return f"Query result : {self.full_query} \nErreur : {self.error_code} ({self.error_detail}) \nInstances : { len(self.result_instances)if self.result_instances else 0 }"


