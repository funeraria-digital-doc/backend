from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from groups.serealizers import GroupCreateSerializer, GroupUpdateSerializer
from rest_framework.parsers import JSONParser
from groups.models import Group


@api_view(['POST'])
def create(request, *args, **kwargs):
    """
    This text is the description for this API.

    ---
    parameters:
    - name: group name
      description: Group name
      required: true
      type: string
      paramType: body
    """
    data = JSONParser().parse(request)
    serializer = GroupCreateSerializer(data=data)
    #serializer = GroupCreateSerializer(data=request.data)
    group = {}
    try:
        if serializer.is_valid():
            try:
                serializer.save()
                group['group']  = serializer.data
                group['msg']  = "Group created successfully"
            except Exception as e:
                group['error']   = serializer.errors
                return Response(group, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
        else: 
            group['error'] = serializer.errors
    except Exception as e:
        group['error']   = "erro no is_valid"
        #raise serializer.errors
    return Response({'message' : group}, status = status.HTTP_200_OK)

@api_view(['GET'])
def view(request, *args, **kwargs):
    group = Group.objects.filter(pk=kwargs.get('pk')).values().first()
    if group is None:
        return Response({"error" : "Group does not exist!"}, status = status.HTTP_200_OK)
    return Response(group, status = status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def update(request, *args, **kwargs):
    group = Group.objects.filter(pk=kwargs.get('pk')).first()  
    serializer = GroupUpdateSerializer(data = request.data,instance=group)   
    if serializer.is_valid():
        if group is None:
                return Response({"error" : "Group does not exist!"}, status = status.HTTP_404_NOT_FOUND)
        try:            
            serializer.update(instance = group, validated_data=serializer.validated_data)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except:
            return Response({'error' : "something went wrong updating group","data" : serializer.errors}, status = status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error' : serializer.errors}, status = status.HTTP_400_BAD_REQUEST)   
   
@api_view(['DELETE'])
def remove(request, *args, **kwargs):
    group = Group.objects.filter(id=kwargs.get('pk')).first()
    if group is None:
        return Response({"error" : "Group does not exist!"},status=status.HTTP_404_NOT_FOUND)
    group.delete()
    return Response({"success" : "Group deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def list(request, *args, **kwargs):
    groups = Group.objects.all().values()
    return Response(groups, status = status.HTTP_200_OK)



