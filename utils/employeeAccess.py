def employeeAccess(status: str, point: int,):
    status = status.split()
    if len(status) == 1:
        return True
    if len(status) >= 2:
        if int(status[1]) == point:
            return True
        else:
            return False
