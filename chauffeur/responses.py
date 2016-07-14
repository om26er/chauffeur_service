from rest_framework.response import Response
from rest_framework import status


def Forbidden(data=None):
    return Response(data=data, status=status.HTTP_403_FORBIDDEN)


def BadRequest(data=None):
    return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


def NotModified(data=None):
    return Response(data=data, status=status.HTTP_304_NOT_MODIFIED)


def Ok(data=None):
    return Response(data=data, status=status.HTTP_200_OK)


def Conflict():
    return Response(status=status.HTTP_409_CONFLICT)
